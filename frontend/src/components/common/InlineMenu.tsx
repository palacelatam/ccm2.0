import React, { useEffect, useRef } from 'react';
import './InlineMenu.css';

export interface InlineMenuItem {
  label: string;
  action: () => void;
  icon?: string;
  className?: string;
  disabled?: boolean;
}

interface InlineMenuProps {
  items: (InlineMenuItem | 'separator')[];
  position: { x: number; y: number };
  onClose: () => void;
}

const InlineMenu: React.FC<InlineMenuProps> = ({ items, position, onClose }) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    // Add event listeners
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    // Position menu to avoid going off-screen
    if (menuRef.current) {
      const menu = menuRef.current;
      const menuRect = menu.getBoundingClientRect();
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;

      // Adjust horizontal position if menu would go off right edge
      if (position.x + menuRect.width > windowWidth) {
        menu.style.left = `${position.x - menuRect.width}px`;
      } else {
        menu.style.left = `${position.x}px`;
      }

      // Adjust vertical position if menu would go off bottom edge
      if (position.y + menuRect.height > windowHeight) {
        menu.style.top = `${position.y - menuRect.height}px`;
      } else {
        menu.style.top = `${position.y}px`;
      }
    }

    // Cleanup event listeners
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [position, onClose]);

  return (
    <div 
      ref={menuRef}
      className="inline-menu"
      style={{
        position: 'fixed',
        left: position.x,
        top: position.y,
        zIndex: 9999
      }}
    >
      {items.map((item, index) => {
        if (item === 'separator') {
          return <div key={`separator-${index}`} className="inline-menu-separator" />;
        }

        return (
          <div
            key={index}
            className={`inline-menu-item ${item.disabled ? 'disabled' : ''} ${item.className || ''}`}
            onClick={() => {
              if (!item.disabled) {
                item.action();
                onClose();
              }
            }}
          >
            {item.icon && <span className="inline-menu-icon">{item.icon}</span>}
            <span className="inline-menu-label">{item.label}</span>
          </div>
        );
      })}
    </div>
  );
};

export default InlineMenu;