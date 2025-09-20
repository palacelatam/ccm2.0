#!/usr/bin/env python3
"""
Client Data Cleanup Script
Removes all email and match documents and resets matched trades to unmatched status
"""

import sys
import os
import logging
from typing import Optional

# Add the backend/src directory to the path so we can import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_src_dir = os.path.join(os.path.dirname(script_dir), 'backend', 'src')
sys.path.append(backend_src_dir)

from config.firebase_config import get_cmek_firestore_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClientDataCleaner:
    def __init__(self):
        self.db = get_cmek_firestore_client()
        
    def cleanup_client_data(self, client_id: str, confirm: bool = False) -> dict:
        """
        Clean up all emails, matches, and reset matched trades for a client
        
        Args:
            client_id: The client ID to clean up
            confirm: If True, actually perform the cleanup
            
        Returns:
            Dictionary with counts of what was cleaned up
        """
        results = {
            'emails_deleted': 0,
            'matches_deleted': 0,
            'trades_reset': 0,
            'errors': []
        }
        
        if not confirm:
            logger.info("DRY RUN MODE - No changes will be made")
            
        try:
            # Check if client exists
            client_doc = self.db.collection('clients').document(client_id).get()
            if not client_doc.exists:
                logger.error(f"Client '{client_id}' does not exist")
                return results
                
            logger.info(f"Found client: {client_id}")
            
            # 1. Delete all email documents
            logger.info("Deleting email documents...")
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            emails_docs = list(emails_ref.stream())
            
            for email_doc in emails_docs:
                if confirm:
                    email_doc.reference.delete()
                results['emails_deleted'] += 1
                logger.info(f"{'Deleted' if confirm else 'Would delete'} email: {email_doc.id}")
            
            # 2. Delete all match documents
            logger.info("Deleting match documents...")
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            matches_docs = list(matches_ref.stream())
            
            for match_doc in matches_docs:
                if confirm:
                    match_doc.reference.delete()
                results['matches_deleted'] += 1
                logger.info(f"{'Deleted' if confirm else 'Would delete'} match: {match_doc.id}")
            
            # 3. Reset matched and confirmed_via_portal trades to unmatched
            logger.info("Resetting matched and confirmed_via_portal trades to unmatched...")
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')

            # Query for trades with status "matched" and "confirmed_via_portal"
            # Firestore doesn't support OR queries, so we need two separate queries
            matched_trades = list(trades_ref.where('status', '==', 'matched').stream())
            confirmed_trades = list(trades_ref.where('status', '==', 'confirmed_via_portal').stream())

            # Combine both results
            all_processed_trades = matched_trades + confirmed_trades

            for trade_doc in all_processed_trades:
                trade_data = trade_doc.to_dict()
                trade_number = trade_data.get('TradeNumber', 'Unknown')
                
                if confirm:
                    # Reset the trade status and clear match-related fields
                    update_data = {
                        'status': 'unmatched',
                        'matched': False,
                        'match_id': None,
                        'matched_at': None,
                        'matched_by': None
                    }
                    trade_doc.reference.update(update_data)
                    
                results['trades_reset'] += 1
                logger.info(f"{'Reset' if confirm else 'Would reset'} trade: {trade_doc.id} ({trade_number})")
            
            # Summary
            logger.info("="*60)
            logger.info("CLEANUP SUMMARY:")
            logger.info(f"  Emails deleted: {results['emails_deleted']}")
            logger.info(f"  Matches deleted: {results['matches_deleted']}")
            logger.info(f"  Trades reset to unmatched: {results['trades_reset']}")
            
            if not confirm:
                logger.info("\nThis was a DRY RUN. Use option 2 to actually perform the cleanup.")
            else:
                logger.info("\nCleanup completed successfully!")
                
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            
        return results
    
    def get_client_stats(self, client_id: str) -> dict:
        """Get current statistics for a client before cleanup"""
        stats = {
            'emails_count': 0,
            'matches_count': 0,
            'processed_trades_count': 0,
            'total_trades_count': 0
        }
        
        try:
            # Check if client exists
            client_doc = self.db.collection('clients').document(client_id).get()
            if not client_doc.exists:
                logger.error(f"Client '{client_id}' does not exist")
                return stats
            
            # Count emails
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            stats['emails_count'] = len(list(emails_ref.stream()))
            
            # Count matches
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            stats['matches_count'] = len(list(matches_ref.stream()))
            
            # Count trades
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            all_trades = list(trades_ref.stream())
            stats['total_trades_count'] = len(all_trades)
            
            # Count processed trades (matched + confirmed_via_portal)
            processed_trades = [t for t in all_trades if t.to_dict().get('status') in ['matched', 'confirmed_via_portal']]
            stats['processed_trades_count'] = len(processed_trades)
            
        except Exception as e:
            logger.error(f"Error getting client stats: {str(e)}")
            
        return stats


def main():
    print("Client Data Cleanup Script")
    print("=" * 50)
    
    # Prompt for client ID
    client_id = input("Enter the client ID to clean up: ").strip()
    if not client_id:
        print("❌ Client ID is required")
        sys.exit(1)
    
    # Ask if they want to confirm the cleanup
    print("\nChoose cleanup mode:")
    print("1. Dry run (preview only - safe)")
    print("2. Actual cleanup (will delete data)")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "1":
            confirm = False
            break
        elif choice == "2":
            confirm = True
            break
        else:
            print("Please enter 1 or 2")
    
    cleaner = ClientDataCleaner()
    
    # Show current stats
    print("\nCurrent client statistics:")
    stats = cleaner.get_client_stats(client_id)
    if stats['emails_count'] == 0 and stats['matches_count'] == 0 and stats['processed_trades_count'] == 0:
        print(f"  Client '{client_id}' has no data to clean up")
        return

    print(f"  Emails: {stats['emails_count']}")
    print(f"  Matches: {stats['matches_count']}")
    print(f"  Processed trades (matched + confirmed via portal): {stats['processed_trades_count']}")
    print(f"  Total trades: {stats['total_trades_count']}")
    print()
    
    if not confirm:
        print("⚠️  DRY RUN MODE - No actual changes will be made")
        print("   Run again and choose option 2 to actually perform the cleanup")
        print()
    else:
        print("🚨 DANGER: This will permanently delete data!")
        response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled.")
            return
        print()
    
    # Perform cleanup
    results = cleaner.cleanup_client_data(client_id, confirm)
    
    if results['errors']:
        print(f"\n❌ Cleanup completed with {len(results['errors'])} errors:")
        for error in results['errors']:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ Cleanup completed successfully!")


if __name__ == "__main__":
    main()