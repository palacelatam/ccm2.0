import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import Papa from 'papaparse';
import ReactEcharts from 'echarts-for-react';
import './FXAnalytics.css';

interface TradeData {
  'Trade ID': string;
  'Client Name': string;
  'Counterparty Name': string;
  'Trade Date': string;
  'Value Date': string;
  'Product Type': string;
  'Currency Pair': string;
  'Notional Amount': string;
  'Rate': string;
  'Side': string;
}

interface RankingData {
  bank: string;
  volume: number;
  tradeCount: number;
  marketShare: number;
  averageDealSize: number;
  isCurrentBank: boolean;
}

interface TrendData {
  date: string;
  rank: number;
  volume: number;
}

const FXAnalytics: React.FC = () => {
  const { t } = useTranslation();
  const [tradeData, setTradeData] = useState<TradeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [clientSearchTerm, setClientSearchTerm] = useState<string>('');
  const [showClientDropdown, setShowClientDropdown] = useState<boolean>(false);
  const [selectedProduct, setSelectedProduct] = useState<string>('All');
  const [selectedCurrencyPair, setSelectedCurrencyPair] = useState<string>('All');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30');
  const [currentBank] = useState<string>('Banco ABC');
  
  // Search filters for missed opportunities
  const [searchClient, setSearchClient] = useState<string>('');
  const [searchClientTerm, setSearchClientTerm] = useState<string>('');
  const [showSearchDropdown, setShowSearchDropdown] = useState<boolean>(false);
  const [searchProduct, setSearchProduct] = useState<string>('');
  const [searchCurrencyPair, setSearchCurrencyPair] = useState<string>('');
  const [searchDate, setSearchDate] = useState<string>('');
  const [searchVolume, setSearchVolume] = useState<string>('');
  const [searchDirection, setSearchDirection] = useState<string>('');
  const [searchYourQuote, setSearchYourQuote] = useState<string>('');
  const [searchResults, setSearchResults] = useState<TradeData[]>([]);
  const [missedOpportunitiesExpanded, setMissedOpportunitiesExpanded] = useState<boolean>(false);

  useEffect(() => {
    loadTradeData();
  }, []);

  const loadTradeData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/tradedata.csv');
      const csvText = await response.text();
      
      Papa.parse(csvText, {
        header: true,
        complete: (results) => {
          setTradeData(results.data as TradeData[]);
          setLoading(false);
        },
        error: (error: any) => {
          console.error('Error parsing CSV:', error);
          setLoading(false);
        }
      });
    } catch (error) {
      console.error('Error loading CSV:', error);
      setLoading(false);
    }
  };

  const clients = useMemo(() => {
    const uniqueClients = [...new Set(tradeData.map(trade => trade['Client Name']))];
    return uniqueClients.filter(client => client && client.trim() !== '').sort();
  }, [tradeData]);

  const filteredClients = useMemo(() => {
    if (!clientSearchTerm) return clients;
    const searchLower = clientSearchTerm.toLowerCase();
    return clients.filter(client => 
      client.toLowerCase().includes(searchLower)
    );
  }, [clients, clientSearchTerm]);

  const handleClientSelect = (client: string) => {
    setSelectedClient(client);
    setClientSearchTerm(client === '' ? '' : client);
    setShowClientDropdown(false);
  };

  const handleClientSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setClientSearchTerm(e.target.value);
    setShowClientDropdown(true);
    if (e.target.value === '') {
      setSelectedClient('');
    }
  };

  const filteredSearchClients = useMemo(() => {
    if (!searchClientTerm) return clients;
    const searchLower = searchClientTerm.toLowerCase();
    return clients.filter(client => 
      client.toLowerCase().includes(searchLower)
    );
  }, [clients, searchClientTerm]);

  const handleSearchClientSelect = (client: string) => {
    setSearchClient(client);
    setSearchClientTerm(client === '' ? '' : client);
    setShowSearchDropdown(false);
  };

  const handleSearchClientChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchClientTerm(e.target.value);
    setShowSearchDropdown(true);
    if (e.target.value === '') {
      setSearchClient('');
    }
  };

  const performSearch = () => {
    let results = [...tradeData];
    
    // Filter by client
    if (searchClient) {
      results = results.filter(trade => trade['Client Name'] === searchClient);
    }
    
    // Filter by product
    if (searchProduct) {
      results = results.filter(trade => trade['Product Type'] === searchProduct);
    }
    
    // Filter by currency pair
    if (searchCurrencyPair) {
      results = results.filter(trade => trade['Currency Pair'] === searchCurrencyPair);
    }
    
    // Filter by date
    if (searchDate) {
      results = results.filter(trade => trade['Trade Date'] === searchDate);
    }
    
    // Filter by volume
    if (searchVolume) {
      const targetVolume = parseFloat(searchVolume) * 1000000; // Convert from millions
      results = results.filter(trade => {
        const tradeVolume = parseFloat(trade['Notional Amount']) || 0;
        return Math.abs(tradeVolume - targetVolume) < (targetVolume * 0.1); // Within 10% tolerance
      });
    }
    
    // Filter by direction
    if (searchDirection) {
      results = results.filter(trade => trade['Side'] === searchDirection);
    }
    
    setSearchResults(results);
  };

  const clearSearch = () => {
    setSearchClient('');
    setSearchClientTerm('');
    setSearchProduct('');
    setSearchCurrencyPair('');
    setSearchDate('');
    setSearchVolume('');
    setSearchDirection('');
    setSearchYourQuote('');
    setSearchResults([]);
  };

  const products = useMemo(() => {
    const uniqueProducts = [...new Set(tradeData.map(trade => trade['Product Type']))];
    return ['All', ...uniqueProducts.filter(product => product && product.trim() !== '')];
  }, [tradeData]);

  const directions = useMemo(() => {
    const uniqueDirections = [...new Set(tradeData.map(trade => trade['Side']))];
    return ['All', ...uniqueDirections.filter(direction => direction && direction.trim() !== '')];
  }, [tradeData]);

  const calculateRateDifference = (tradeRate: number, yourQuote: number, direction: string): number => {
    if (!yourQuote) return 0;
    
    // For Buy: positive difference means you quoted better (lower rate)
    // For Sell: positive difference means you quoted better (higher rate)
    if (direction === 'Buy') {
      return yourQuote - tradeRate; // Positive = you were cheaper
    } else if (direction === 'Sell') {
      return tradeRate - yourQuote; // Positive = you were more expensive
    }
    return tradeRate - yourQuote; // Default comparison
  };

  const getRateDifferenceColor = (difference: number): string => {
    if (difference > 0) return '#22c55e'; // Green - you quoted better
    if (difference < 0) return '#ef4444'; // Red - you quoted worse
    return 'var(--text-primary)'; // White/default - same rate
  };

  const currencyPairs = useMemo(() => {
    const uniquePairs = [...new Set(tradeData.map(trade => trade['Currency Pair']))];
    return ['All', ...uniquePairs.filter(pair => pair && pair.trim() !== '').sort()];
  }, [tradeData]);

  const filteredData = useMemo(() => {
    let filtered = [...tradeData];
    
    if (selectedClient) {
      filtered = filtered.filter(trade => trade['Client Name'] === selectedClient);
    }
    
    if (selectedProduct !== 'All') {
      filtered = filtered.filter(trade => trade['Product Type'] === selectedProduct);
    }
    
    if (selectedCurrencyPair !== 'All') {
      filtered = filtered.filter(trade => trade['Currency Pair'] === selectedCurrencyPair);
    }
    
    const cutoffDate = new Date();
    const days = parseInt(selectedPeriod);
    cutoffDate.setTime(cutoffDate.getTime() - (days * 24 * 60 * 60 * 1000));
    filtered = filtered.filter(trade => {
      const tradeDate = new Date(trade['Trade Date']);
      return tradeDate >= cutoffDate;
    });
    
    return filtered;
  }, [tradeData, selectedClient, selectedProduct, selectedCurrencyPair, selectedPeriod]);

  const rankingData = useMemo((): RankingData[] => {
    const bankVolumes: { [key: string]: { volume: number; count: number } } = {};
    
    filteredData.forEach(trade => {
      const bank = trade['Counterparty Name'];
      const amount = parseFloat(trade['Notional Amount']) || 0;
      
      if (!bankVolumes[bank]) {
        bankVolumes[bank] = { volume: 0, count: 0 };
      }
      
      bankVolumes[bank].volume += amount;
      bankVolumes[bank].count += 1;
    });
    
    const totalVolume = Object.values(bankVolumes).reduce((sum, data) => sum + data.volume, 0);
    
    const rankings = Object.entries(bankVolumes).map(([bank, data]) => ({
      bank: bank === currentBank ? 'You' : bank.startsWith('Bank') ? `Competitor ${bank.charAt(bank.length - 1)}` : bank,
      volume: data.volume,
      tradeCount: data.count,
      marketShare: (data.volume / totalVolume) * 100,
      averageDealSize: data.count > 0 ? data.volume / data.count : 0,
      isCurrentBank: bank === currentBank
    }));
    
    return rankings.sort((a, b) => b.volume - a.volume);
  }, [filteredData, currentBank]);

  const trendData = useMemo((): TrendData[] => {
    const dailyRankings: { [date: string]: { [bank: string]: number } } = {};
    
    filteredData.forEach(trade => {
      const date = trade['Trade Date'];
      const bank = trade['Counterparty Name'];
      const amount = parseFloat(trade['Notional Amount']) || 0;
      
      if (!dailyRankings[date]) {
        dailyRankings[date] = {};
      }
      
      if (!dailyRankings[date][bank]) {
        dailyRankings[date][bank] = 0;
      }
      
      dailyRankings[date][bank] += amount;
    });
    
    const trends: TrendData[] = [];
    
    Object.entries(dailyRankings).forEach(([date, volumes]) => {
      const sortedBanks = Object.entries(volumes)
        .sort((a, b) => b[1] - a[1])
        .map(([bank]) => bank);
      
      const currentBankRank = sortedBanks.indexOf(currentBank) + 1;
      const currentBankVolume = volumes[currentBank] || 0;
      
      if (currentBankRank > 0) {
        trends.push({
          date,
          rank: currentBankRank,
          volume: currentBankVolume
        });
      }
    });
    
    return trends.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [filteredData, currentBank]);

  const barChartOption = {
    title: {
      text: t('bank.analytics.counterpartyRankings'),
      left: 'center',
      textStyle: {
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const dataIndex = params[0].dataIndex;
        const ranking = rankingData[dataIndex];
        return `
          <div>
            <strong>${ranking.bank}</strong><br/>
            Volume: $${(ranking.volume / 1000000).toFixed(2)}M<br/>
            Market Share: ${ranking.marketShare.toFixed(1)}%<br/>
            Trade Count: ${ranking.tradeCount}<br/>
            Avg Deal Size: $${(ranking.averageDealSize / 1000000).toFixed(2)}M
          </div>
        `;
      }
    },
    xAxis: {
      type: 'category',
      data: rankingData.map(d => d.bank),
      axisLabel: {
        rotate: 45,
        color: '#ffffff'
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      }
    },
    yAxis: [{
      type: 'value',
      name: 'Volume ($M)',
      nameTextStyle: {
        color: '#ffffff'
      },
      axisLabel: {
        formatter: (value: number) => `$${(value / 1000000).toFixed(0)}M`,
        color: '#ffffff'
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      },
      splitLine: {
        lineStyle: { color: '#444444' }
      }
    }, {
      type: 'value',
      name: 'Avg Deal Size ($M)',
      nameTextStyle: {
        color: '#ffffff'
      },
      axisLabel: {
        formatter: (value: number) => `$${(value / 1000000).toFixed(1)}M`,
        color: '#ffffff'
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      },
      splitLine: {
        show: false
      }
    }],
    series: [{
      name: 'Volume',
      type: 'bar',
      yAxisIndex: 0,
      data: rankingData.map(d => ({
        value: d.volume,
        itemStyle: {
          color: d.isCurrentBank ? '#FFB74D' : '#6B7280'
        }
      }))
    }, {
      name: 'Avg Deal Size',
      type: 'line',
      yAxisIndex: 1,
      data: rankingData.map(d => d.averageDealSize),
      lineStyle: {
        color: '#00BCD4',
        width: 3
      },
      itemStyle: {
        color: '#00BCD4'
      },
      symbol: 'circle',
      symbolSize: 6
    }]
  };

  const lineChartOption = {
    title: {
      text: t('bank.analytics.rankingTrend'),
      left: 'center',
      top: 10,
      textStyle: {
        color: '#ffffff'
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '25%',
      top: '15%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0];
        return `
          <div>
            Date: ${data.name}<br/>
            Rank: #${data.value}<br/>
            Volume: $${(trendData[data.dataIndex].volume / 1000000).toFixed(2)}M
          </div>
        `;
      }
    },
    xAxis: {
      type: 'category',
      data: trendData.map(d => d.date),
      axisLabel: {
        color: '#ffffff',
        rotate: 0,
        interval: 0,
        fontSize: 11,
        margin: 10
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      },
      axisTick: {
        show: true,
        lineStyle: { color: '#ffffff' }
      }
    },
    yAxis: {
      type: 'value',
      inverse: true,
      min: 1,
      max: Math.max(...trendData.map(d => d.rank), 5),
      interval: 1,
      minInterval: 1,
      axisLabel: {
        formatter: (value: number) => `#${Math.round(value)}`,
        color: '#ffffff'
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      },
      splitLine: {
        lineStyle: { color: '#444444' }
      }
    },
    series: [{
      type: 'line',
      data: trendData.map(d => d.rank),
      smooth: true,
      lineStyle: {
        width: 3,
        color: '#4CAF50'
      },
      itemStyle: {
        color: '#4CAF50'
      }
    }]
  };

  const pieChartOption = {
    title: {
      text: t('bank.analytics.marketShareDistribution'),
      left: 'center',
      textStyle: {
        color: '#ffffff'
      }
    },
    legend: {
      orient: 'horizontal',
      bottom: '10px',
      textStyle: {
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {d}%'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      label: {
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 'normal'
      },
      labelLine: {
        lineStyle: {
          color: '#ffffff'
        }
      },
      data: rankingData.map(d => ({
        name: d.bank,
        value: d.marketShare,
        itemStyle: {
          color: d.isCurrentBank ? '#4CAF50' : undefined
        }
      }))
    }]
  };

  const currentRank = rankingData.findIndex(r => r.isCurrentBank) + 1;
  const totalRanks = rankingData.length;
  const yourVolume = rankingData.find(r => r.isCurrentBank)?.volume || 0;
  const yourMarketShare = rankingData.find(r => r.isCurrentBank)?.marketShare || 0;
  const yourTradeCount = rankingData.find(r => r.isCurrentBank)?.tradeCount || 0;

  if (loading) {
    return (
      <div className="fx-analytics">
        <div className="loading-state">
          <p>Loading trade data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fx-analytics">
      <div className="analytics-header">
        <div className="admin-title">FX Analytics</div>
      </div>

      <div className={`analytics-layout ${missedOpportunitiesExpanded ? 'with-expanded-sidebar' : ''}`}>
        <div className="main-content">
          <div className="filters-section">
            <div className="filter-group">
              <label>{t('bank.analytics.client', 'Client')}</label>
              <div className="searchable-dropdown">
                <input
                  type="text"
                  value={clientSearchTerm}
                  onChange={handleClientSearchChange}
                  onFocus={() => setShowClientDropdown(true)}
                  onBlur={() => setTimeout(() => setShowClientDropdown(false), 200)}
                  placeholder={t('bank.analytics.searchClients', 'Search clients...')}
                  className="client-search-input"
                />
                {showClientDropdown && (
                  <div className={`dropdown-menu ${!clientSearchTerm ? 'full-list' : ''}`}>
                    <div 
                      className="dropdown-item"
                      onClick={() => handleClientSelect('')}
                    >
                      {t('bank.analytics.allClients')}
                    </div>
                    {filteredClients.map(client => (
                      <div 
                        key={client} 
                        className="dropdown-item"
                        onClick={() => handleClientSelect(client)}
                      >
                        {client}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="filter-group">
              <label>{t('bank.analytics.product', 'Product')}</label>
              <select 
                value={selectedProduct} 
                onChange={(e) => setSelectedProduct(e.target.value)}
              >
                {products.map(product => (
                  <option key={product} value={product}>
                    {product === 'All' ? t('bank.analytics.allProducts') : product}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>{t('bank.analytics.currencyPair', 'Currency Pair')}</label>
              <select 
                value={selectedCurrencyPair} 
                onChange={(e) => setSelectedCurrencyPair(e.target.value)}
              >
                {currencyPairs.map(pair => (
                  <option key={pair} value={pair}>
                    {pair === 'All' ? t('bank.analytics.allCurrencyPairs', 'All Pairs') : pair}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>{t('bank.analytics.period', 'Period')}</label>
              <select 
                value={selectedPeriod} 
                onChange={(e) => setSelectedPeriod(e.target.value)}
              >
                <option value="7">{t('bank.analytics.last7Days')}</option>
                <option value="30">{t('bank.analytics.last30Days')}</option>
                <option value="90">{t('bank.analytics.last90Days')}</option>
                <option value="365">{t('bank.analytics.lastYear')}</option>
              </select>
            </div>
          </div>

          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-label">{t('bank.analytics.yourRank', 'Your Rank')}</div>
              <div className="metric-value">{currentRank > 0 ? `#${currentRank}` : 'N/A'}</div>
              <div className="metric-subtext">{t('bank.analytics.outOf')} {totalRanks} {t('bank.analytics.banks')}</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">{t('bank.analytics.totalVolume', 'Total Volume')}</div>
              <div className="metric-value">${(yourVolume / 1000000).toFixed(2)}M</div>
              <div className="metric-subtext">{yourTradeCount} {t('bank.analytics.trades')}</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">{t('bank.analytics.marketShare', 'Market Share')}</div>
              <div className="metric-value">{yourMarketShare.toFixed(1)}%</div>
              <div className="metric-subtext">{t('bank.analytics.ofTotalVolume')}</div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-container">
              <ReactEcharts option={barChartOption} style={{ height: '400px' }} />
            </div>

            <div className="chart-container">
              <ReactEcharts option={pieChartOption} style={{ height: '400px' }} />
            </div>

            <div className="chart-container full-width">
              <ReactEcharts option={lineChartOption} style={{ height: '500px' }} />
            </div>
          </div>
        </div>

        <div className={`sidebar ${missedOpportunitiesExpanded ? 'expanded' : 'collapsed'}`}>
          <div 
            className="missed-opportunities"
            onClick={!missedOpportunitiesExpanded ? () => setMissedOpportunitiesExpanded(true) : undefined}
          >
            <div className="missed-opportunities-header">
              {missedOpportunitiesExpanded && (
                <>
                  <h3>{t('bank.analytics.missedTrades.title', 'Missed Trades')}</h3>
                  <button 
                    className="expand-toggle"
                    onClick={() => setMissedOpportunitiesExpanded(false)}
                    title="Collapse"
                  >
                    ▶
                  </button>
                </>
              )}
              {!missedOpportunitiesExpanded && (
                <div className="expand-toggle">
                  ◀
                </div>
              )}
            </div>
            
            {missedOpportunitiesExpanded && (
              <div className="search-filters">
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.client', 'Client')}</label>
                  <div className="searchable-dropdown-small">
                    <input
                      type="text"
                      value={searchClientTerm}
                      onChange={handleSearchClientChange}
                      onFocus={() => setShowSearchDropdown(true)}
                      onBlur={() => setTimeout(() => setShowSearchDropdown(false), 200)}
                      placeholder={t('bank.analytics.missedTrades.searchClients', 'Search clients...')}
                      className="filter-input"
                    />
                    {showSearchDropdown && (
                      <div className={`dropdown-menu-small ${!searchClientTerm ? 'full-list' : ''}`}>
                        <div 
                          className="dropdown-item-small"
                          onClick={() => handleSearchClientSelect('')}
                        >
                          {t('bank.analytics.missedTrades.allClients', 'All Clients')}
                        </div>
                        {filteredSearchClients.map(client => (
                          <div 
                            key={client} 
                            className="dropdown-item-small"
                            onClick={() => handleSearchClientSelect(client)}
                          >
                            {client}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.product', 'Product')}</label>
                  <select 
                    className="filter-select"
                    value={searchProduct}
                    onChange={(e) => setSearchProduct(e.target.value)}
                  >
                    <option value="">{t('bank.analytics.missedTrades.allProducts', 'All Products')}</option>
                    {products.slice(1).map(product => (
                      <option key={product} value={product}>{product}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.currencyPair', 'Currency Pair')}</label>
                  <select 
                    className="filter-select"
                    value={searchCurrencyPair}
                    onChange={(e) => setSearchCurrencyPair(e.target.value)}
                  >
                    <option value="">{t('bank.analytics.missedTrades.allPairs', 'All Pairs')}</option>
                    {currencyPairs.slice(1).map(pair => (
                      <option key={pair} value={pair}>{pair}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.tradeDate', 'Trade Date')}</label>
                  <input 
                    type="date" 
                    className="filter-input"
                    value={searchDate}
                    onChange={(e) => setSearchDate(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.volume', 'Volume ($M)')}</label>
                  <input 
                    type="number" 
                    placeholder="e.g. 5.5"
                    className="filter-input"
                    step="0.1"
                    min="0"
                    value={searchVolume}
                    onChange={(e) => setSearchVolume(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.direction', 'Direction')}</label>
                  <select 
                    className="filter-select"
                    value={searchDirection}
                    onChange={(e) => setSearchDirection(e.target.value)}
                  >
                    <option value="">{t('bank.analytics.missedTrades.allDirections', 'All Directions')}</option>
                    {directions.slice(1).map(direction => (
                      <option key={direction} value={direction}>{direction}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="filter-row">
                <div className="filter-group-small">
                  <label>{t('bank.analytics.missedTrades.yourQuote', 'Your Quote')}</label>
                  <input 
                    type="number" 
                    placeholder="e.g. 950.5"
                    className="filter-input"
                    step="0.0001"
                    min="0"
                    value={searchYourQuote}
                    onChange={(e) => setSearchYourQuote(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="search-buttons">
                <button className="search-button" onClick={performSearch}>
                  {t('bank.analytics.missedTrades.searchTrades', 'Search Trades')}
                </button>
                <button className="clear-button" onClick={clearSearch}>
                  {t('bank.analytics.missedTrades.clearSearch', 'Clear')}
                </button>
              </div>
            </div>
            )}
            
            {missedOpportunitiesExpanded && (
              <div className="opportunities-table">
              <div className="table-header">
                <div className="header-cell">{t('bank.analytics.missedTrades.client', 'Client')}</div>
                <div className="header-cell">{t('bank.analytics.missedTrades.product', 'Product')}</div>
                <div className="header-cell">{t('bank.analytics.missedTrades.currencyPair', 'Currency Pair')}</div>
                <div className="header-cell">{t('bank.analytics.missedTrades.volume', 'Volume')}</div>
                <div className="header-cell">{t('bank.analytics.missedTrades.direction', 'Direction')}</div>
                <div className="header-cell">{t('bank.analytics.missedTrades.counterparty', 'Counterparty')}</div>
                <div className="header-cell">{t('bank.analytics.missedTrades.rate', 'Rate')}</div>
                {searchYourQuote && <div className="header-cell">{t('bank.analytics.missedTrades.difference', 'Difference')}</div>}
                <div className="header-cell">{t('bank.analytics.missedTrades.date', 'Date')}</div>
              </div>
              
              {searchResults.length === 0 && (searchClient || searchProduct || searchCurrencyPair || searchDate || searchVolume) ? (
                <div className="search-results-placeholder">
                  <p>{t('bank.analytics.missedTrades.noTradesFound', 'No trades found matching your search criteria.')}</p>
                </div>
              ) : searchResults.length === 0 ? (
                <div className="search-results-placeholder">
                  <p>{t('bank.analytics.missedTrades.useFilters', 'Use the search filters above to find trades matching your criteria.')}</p>
                </div>
              ) : (
                searchResults.slice(0, 20).map(trade => {
                  const tradeRate = parseFloat(trade['Rate']);
                  const yourQuote = parseFloat(searchYourQuote);
                  const difference = calculateRateDifference(tradeRate, yourQuote, trade['Side']);
                  const differenceColor = getRateDifferenceColor(difference);
                  
                  return (
                    <div key={trade['Trade ID']} className="table-row">
                      <div className="table-cell">{trade['Client Name']}</div>
                      <div className="table-cell">{trade['Product Type']}</div>
                      <div className="table-cell">{trade['Currency Pair']}</div>
                      <div className="table-cell">${(parseFloat(trade['Notional Amount']) / 1000000).toFixed(2)}M</div>
                      <div className="table-cell">{trade['Side']}</div>
                      <div className="table-cell">
                        {trade['Counterparty Name'] === currentBank ? 'You' : 
                         trade['Counterparty Name'].startsWith('Bank') ? 
                         `Competitor ${trade['Counterparty Name'].charAt(trade['Counterparty Name'].length - 1)}` : 
                         trade['Counterparty Name']}
                      </div>
                      <div className="table-cell">{tradeRate.toFixed(4)}</div>
                      {searchYourQuote && (
                        <div className="table-cell" style={{ color: differenceColor, fontWeight: '600' }}>
                          {difference > 0 ? '+' : ''}{difference.toFixed(4)}
                        </div>
                      )}
                      <div className="table-cell">{trade['Trade Date']}</div>
                    </div>
                  );
                })
              )}
            </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FXAnalytics;