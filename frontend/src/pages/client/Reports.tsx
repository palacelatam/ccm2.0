import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GridReadyEvent, GridApi } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import ReactEcharts from 'echarts-for-react';
import StatusCellRenderer from '../../components/grids/StatusCellRenderer';
import './Reports.css';
import '../../components/grids/StatusCellRenderer.css';

interface ReportData {
  'Trade ID': string;
  'Counterparty': string;
  'Product Type': string;
  'Trade Date': string;
  'Value Date': string;
  'Direction': string;
  'Currency 1': string;
  'Currency 2': string;
  'Amount': string;
  'Forward Price': string;
  'Settlement Type': string;
  'Match Status': string; // Sin Coincidencia, Full Match, Confirmado por Portal
  'Confirmation Status': string; // Confirmation OK, Difference, N/A
  'Discrepant Fields': string; // List of fields with differences
  'Fields Match': string;
  'Email Sent': string;
  'Settlement Sent': string;
  'Confirmation Source': string;
  'Confirmation Email Sent': string;
  'Dispute Email Sent': string;
  'Settlement Instructions Sent': string;
}


const Reports: React.FC = () => {
  const { t } = useTranslation();
  const [reportData, setReportData] = useState<ReportData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDateRange, setSelectedDateRange] = useState<string>('0');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [selectedCounterparty, setSelectedCounterparty] = useState<string>('All');
  const [selectedProduct, setSelectedProduct] = useState<string>('All');
  const [gridApi, setGridApi] = useState<GridApi | null>(null);

  const columnDefs: ColDef[] = useMemo(() => [
    {
      field: 'Trade Date',
      headerName: 'Fecha Operación',
      width: 120,
      sortable: true,
      filter: true
    },
    {
      field: 'Trade ID',
      headerName: 'ID Operación',
      width: 100,
      sortable: true,
      filter: true
    },
    {
      field: 'Match Status',
      headerName: 'Estado Coincidencia',
      width: 180,
      cellRenderer: (params: any) => {
        const getMatchStatusClass = (status: string) => {
          switch (status) {
            case 'Full Match': return 'status-matched';
            case 'Sin Coincidencia': return 'status-unrecognised';
            case 'Confirmado por Portal': return 'status-confirmed-portal';
            default: return 'status-default';
          }
        };
        return (
          <span className={`status-badge ${getMatchStatusClass(params.value)}`}>
            {params.value}
          </span>
        );
      },
      sortable: true,
      filter: true
    },
    {
      field: 'Confirmation Status',
      headerName: 'Estado Confirmación',
      width: 160,
      cellRenderer: (params: any) => {
        const getConfirmationStatusClass = (status: string) => {
          switch (status) {
            case 'Confirmation OK': return 'status-matched';
            case 'Diferencia': return 'status-disputed';
            case 'N/A': return 'status-default';
            default: return 'status-default';
          }
        };
        return (
          <span className={`status-badge ${getConfirmationStatusClass(params.value)}`}>
            {params.value}
          </span>
        );
      },
      sortable: true,
      filter: true
    },
    {
      field: 'Counterparty',
      headerName: 'Contraparte',
      width: 140,
      sortable: true,
      filter: true
    },
    {
      field: 'Product Type',
      headerName: 'Producto',
      width: 100,
      sortable: true,
      filter: true
    },
    {
      field: 'Direction',
      headerName: 'Dirección',
      width: 70,
      sortable: true,
      filter: true
    },
    {
      field: 'Currency Pair',
      headerName: 'Par Monedas',
      width: 110,
      valueGetter: (params) => `${params.data['Currency 1']}/${params.data['Currency 2']}`,
      sortable: true,
      filter: true
    },
    {
      field: 'Amount',
      headerName: 'Monto',
      width: 130,
      valueFormatter: (params) => parseFloat(params.value).toLocaleString(),
      sortable: true,
      filter: true
    },
    {
      field: 'Forward Price',
      headerName: 'Precio',
      width: 100,
      sortable: true,
      filter: true
    },
    {
      field: 'Value Date',
      headerName: 'Fecha Vencimiento',
      width: 120,
      sortable: true,
      filter: true
    },
    {
      field: 'Settlement Type',
      headerName: 'Modalidad',
      width: 140,
      sortable: true,
      filter: true
    },
    {
      field: 'Discrepant Fields',
      headerName: 'Discrepancias',
      width: 180,
      sortable: true,
      filter: true,
      cellRenderer: (params: any) => {
        if (!params.value || params.value === '') {
          return <span style={{ color: '#6b7280' }}>-</span>;
        }
        return <span style={{ color: '#ef4444' }}>{params.value}</span>;
      }
    },
    {
      field: 'Confirmation Email Sent',
      headerName: 'Correos Conf.',
      width: 110,
      sortable: true,
      filter: true,
      cellRenderer: (params: any) => {
        const color = params.value === 'Sí' ? '#22c55e' : '#6b7280';
        return <span style={{ color }}>{params.value}</span>;
      }
    },
    {
      field: 'Settlement Instructions Sent',
      headerName: 'Carta de Instrucción',
      width: 110,
      sortable: true,
      filter: true,
      cellRenderer: (params: any) => {
        const color = params.value === 'Sí' ? '#22c55e' : '#6b7280';
        return <span style={{ color }}>{params.value}</span>;
      }
    }
  ], [t]);


  const onGridReady = (params: GridReadyEvent) => {
    setGridApi(params.api);
  };


  useEffect(() => {
    loadReportData();
  }, []);

  const loadReportData = async () => {
    setLoading(true);

    // Generate 500 trades from May 16, 2025 to October 1, 2025
    const mockData: ReportData[] = [];

    // Helper function to format date as DD/MM/YYYY
    const formatDate = (date: Date): string => {
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    };

    // Helper function to skip weekends
    const getNextWeekday = (date: Date): Date => {
      const newDate = new Date(date);
      const day = newDate.getDay();
      if (day === 6) { // Saturday
        newDate.setDate(newDate.getDate() + 2);
      } else if (day === 0) { // Sunday
        newDate.setDate(newDate.getDate() + 1);
      }
      return newDate;
    };

    // Available counterparties
    const counterparties = ['BCI', 'Itaú', 'Banco ABC', 'Santander', 'Banco Estado', 'Scotiabank'];
    const currencies = [
      ['USD', 'CLP'], ['EUR', 'USD'], ['GBP', 'USD'], ['EUR', 'CLP'], ['USD', 'BRL']
    ];
    const directions = ['Compra', 'Venta'];

    // Start from May 16, 2025
    let currentDate = new Date(2025, 4, 16); // Month is 0-indexed
    const endDate = new Date(2025, 9, 1); // October 1, 2025
    let tradeId = 31510; // Working backwards from 32009

    while (currentDate <= endDate && mockData.length < 500) {
      // Skip weekends
      currentDate = getNextWeekday(currentDate);

      // Generate 3-5 trades per day
      const tradesPerDay = Math.floor(Math.random() * 3) + 3;

      for (let i = 0; i < tradesPerDay && mockData.length < 500; i++) {
        const counterparty = counterparties[Math.floor(Math.random() * counterparties.length)];
        const productType = Math.random() > 0.4 ? 'Spot' : 'Forward';
        const currencyPair = currencies[Math.floor(Math.random() * currencies.length)];
        const direction = directions[Math.floor(Math.random() * directions.length)];
        const amount = (Math.floor(Math.random() * 20) + 1) * 100000; // 100k to 2M

        // Calculate value date
        const valueDate = new Date(currentDate);
        if (productType === 'Spot') {
          valueDate.setDate(valueDate.getDate() + 2);
        } else {
          valueDate.setDate(valueDate.getDate() + 30 + Math.floor(Math.random() * 60));
        }

        // Determine match status (85% Full Match, 10% Portal, 5% Unmatched)
        let matchStatus: string;
        let confirmationStatus: string;
        let discrepantFields: string = '';
        let confirmationEmailSent: string;
        let disputeEmailSent: string = 'No';
        let settlementSent: string;

        const statusRandom = Math.random();
        if (statusRandom < 0.85) {
          matchStatus = 'Full Match';
          // 80% OK, 20% with differences
          if (Math.random() < 0.8) {
            confirmationStatus = 'Confirmation OK';
            confirmationEmailSent = 'Sí';
            settlementSent = 'Sí';
          } else {
            confirmationStatus = 'Diferencia';
            const discrepancies = ['Amount', 'Price', 'Settlement Date', 'Value Date'];
            discrepantFields = discrepancies[Math.floor(Math.random() * discrepancies.length)];
            confirmationEmailSent = 'No';
            disputeEmailSent = 'Sí';
            settlementSent = 'No';
          }
        } else if (statusRandom < 0.95) {
          matchStatus = 'Confirmado por Portal';
          confirmationStatus = 'N/A';
          confirmationEmailSent = 'Sí';
          settlementSent = 'Sí';
        } else {
          matchStatus = 'Sin Coincidencia';
          confirmationStatus = 'N/A';
          confirmationEmailSent = 'No';
          settlementSent = 'No';
        }

        // Calculate price based on currency pair
        let price: string;
        if (currencyPair[1] === 'CLP') {
          price = (920 + Math.random() * 40).toFixed(2); // 920-960 for CLP
        } else if (currencyPair[0] === 'EUR' && currencyPair[1] === 'USD') {
          price = (1.08 + Math.random() * 0.08).toFixed(4); // 1.08-1.16 for EUR/USD
        } else if (currencyPair[0] === 'GBP' && currencyPair[1] === 'USD') {
          price = (1.25 + Math.random() * 0.10).toFixed(4); // 1.25-1.35 for GBP/USD
        } else {
          price = (4.8 + Math.random() * 0.4).toFixed(4); // 4.8-5.2 for USD/BRL
        }

        mockData.push({
          'Trade ID': tradeId.toString(),
          'Counterparty': counterparty,
          'Product Type': productType,
          'Trade Date': formatDate(currentDate),
          'Value Date': formatDate(valueDate),
          'Direction': direction,
          'Currency 1': currencyPair[0],
          'Currency 2': currencyPair[1],
          'Amount': amount.toString(),
          'Forward Price': price,
          'Settlement Type': productType === 'Spot' ? 'Entrega Física' : 'Compensación',
          'Match Status': matchStatus,
          'Confirmation Status': confirmationStatus,
          'Discrepant Fields': discrepantFields,
          'Fields Match': matchStatus === 'Full Match' ? 'Sí' : 'No',
          'Email Sent': confirmationEmailSent,
          'Settlement Sent': settlementSent,
          'Confirmation Source': matchStatus === 'Confirmado por Portal' ? 'Portal' : 'Email',
          'Confirmation Email Sent': confirmationEmailSent,
          'Dispute Email Sent': disputeEmailSent,
          'Settlement Instructions Sent': settlementSent
        });

        tradeId++;
      }

      // Move to next day
      currentDate.setDate(currentDate.getDate() + 1);
    }

    // Sort by trade date descending (most recent first)
    mockData.sort((a, b) => {
      const [dayA, monthA, yearA] = a['Trade Date'].split('/').map(Number);
      const [dayB, monthB, yearB] = b['Trade Date'].split('/').map(Number);
      const dateA = new Date(yearA, monthA - 1, dayA);
      const dateB = new Date(yearB, monthB - 1, dayB);
      return dateB.getTime() - dateA.getTime();
    });

    setTimeout(() => {
      setReportData(mockData);
      setLoading(false);
    }, 500);
  };


  const statuses = useMemo(() => {
    const uniqueStatuses = [...new Set(reportData.map(report => report['Match Status']))];
    return ['All', ...uniqueStatuses.filter(status => status && status.trim() !== '')];
  }, [reportData]);

  const counterparties = useMemo(() => {
    const uniqueCounterparties = [...new Set(reportData.map(report => report['Counterparty']))];
    return ['All', ...uniqueCounterparties.filter(cp => cp && cp.trim() !== '').sort()];
  }, [reportData]);

  const products = useMemo(() => {
    const uniqueProducts = [...new Set(reportData.map(report => report['Product Type']))];
    return ['All', ...uniqueProducts.filter(product => product && product.trim() !== '')];
  }, [reportData]);

  const filteredData = useMemo(() => {
    let filtered = [...reportData];

    // Date range filter
    if (startDate && endDate) {
      // Custom date range
      const startFilterDate = new Date(startDate);
      const endFilterDate = new Date(endDate);
      filtered = filtered.filter(report => {
        // Parse date in DD/MM/YYYY format
        const [day, month, year] = report['Trade Date'].split('/');
        const reportDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
        return reportDate >= startFilterDate && reportDate <= endFilterDate;
      });
    } else if (selectedDateRange !== '0') {
      // Dropdown date range
      const cutoffDate = new Date();
      const days = parseInt(selectedDateRange);
      cutoffDate.setTime(cutoffDate.getTime() - (days * 24 * 60 * 60 * 1000));
      filtered = filtered.filter(report => {
        // Parse date in DD/MM/YYYY format
        const [day, month, year] = report['Trade Date'].split('/');
        const reportDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
        return reportDate >= cutoffDate;
      });
    }

    // Status filter
    if (selectedStatus !== 'All') {
      filtered = filtered.filter(report => report['Match Status'] === selectedStatus);
    }

    // Counterparty filter
    if (selectedCounterparty !== 'All') {
      filtered = filtered.filter(report => report['Counterparty'] === selectedCounterparty);
    }

    // Product filter
    if (selectedProduct !== 'All') {
      filtered = filtered.filter(report => report['Product Type'] === selectedProduct);
    }

    return filtered;
  }, [reportData, selectedDateRange, startDate, endDate, selectedStatus, selectedCounterparty, selectedProduct]);

  // Calculate statistics for summary cards
  const stats = useMemo(() => {
    const total = filteredData.length;
    const fullyMatched = filteredData.filter(r => r['Match Status'] === 'Full Match').length;
    const unmatched = filteredData.filter(r => r['Match Status'] === 'Sin Coincidencia').length;
    const portal = filteredData.filter(r => r['Match Status'] === 'Confirmado por Portal').length;
    const confirmationOK = filteredData.filter(r => r['Confirmation Status'] === 'Confirmation OK').length;
    const differences = filteredData.filter(r => r['Confirmation Status'] === 'Diferencia').length;
    const confirmationEmailsSent = filteredData.filter(r => r['Confirmation Email Sent'] === 'Sí').length;
    const disputeEmailsSent = filteredData.filter(r => r['Dispute Email Sent'] === 'Sí').length;
    const settlementsSent = filteredData.filter(r => r['Settlement Instructions Sent'] === 'Sí').length;

    return {
      total,
      fullyMatched,
      unmatched,
      portal,
      confirmationOK,
      differences,
      matchRate: total > 0 ? ((fullyMatched + portal) / total * 100).toFixed(1) : '0',
      confirmationEmailsSent,
      disputeEmailsSent,
      settlementsSent
    };
  }, [filteredData]);

  // Status distribution chart
  const statusChartOption = {
    title: {
      text: 'Distribución de Estados',
      left: 'center',
      textStyle: {
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      label: {
        color: '#ffffff'
      },
      labelLine: {
        lineStyle: {
          color: '#ffffff'
        }
      },
      data: [
        { value: stats.fullyMatched, name: 'Full Match', itemStyle: { color: '#22c55e' }},
        { value: stats.unmatched, name: 'Sin Coincidencia', itemStyle: { color: '#ef4444' }},
        { value: stats.portal, name: 'Confirmado por Portal', itemStyle: { color: '#00bcd4' }}
      ].filter(item => item.value > 0)
    }]
  };

  // Daily trend chart
  const dailyTrendData = useMemo(() => {
    const dailyStats: { [date: string]: { total: number; matched: number; unmatched: number } } = {};

    filteredData.forEach(report => {
      const date = report['Trade Date'];
      if (!dailyStats[date]) {
        dailyStats[date] = { total: 0, matched: 0, unmatched: 0 };
      }
      dailyStats[date].total++;
      if (report['Match Status'] === 'Full Match' || report['Match Status'] === 'Confirmado por Portal') {
        dailyStats[date].matched++;
      } else if (report['Match Status'] === 'Sin Coincidencia') {
        dailyStats[date].unmatched++;
      }
    });

    return Object.entries(dailyStats)
      .sort((a, b) => {
        // Parse DD/MM/YYYY format properly
        const [dayA, monthA, yearA] = a[0].split('/').map(Number);
        const [dayB, monthB, yearB] = b[0].split('/').map(Number);
        const dateA = new Date(yearA, monthA - 1, dayA);
        const dateB = new Date(yearB, monthB - 1, dayB);
        return dateA.getTime() - dateB.getTime();
      })
      .map(([date, stats]) => ({ date, ...stats }));
  }, [filteredData]);

  const trendChartOption = {
    title: {
      text: 'Tendencia Diaria de Confirmaciones',
      left: 'center',
      textStyle: {
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      bottom: 10,
      textStyle: {
        color: '#ffffff'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dailyTrendData.map(d => d.date),
      axisLabel: {
        color: '#ffffff',
        rotate: 45
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#ffffff'
      },
      axisLine: {
        lineStyle: { color: '#ffffff' }
      },
      splitLine: {
        lineStyle: { color: '#444444' }
      }
    },
    series: [
      {
        name: 'Confirmados',
        type: 'bar',
        stack: 'total',
        data: dailyTrendData.map(d => d.matched),
        itemStyle: { color: '#22c55e' }
      },
      {
        name: 'Sin Confirmar',
        type: 'bar',
        stack: 'total',
        data: dailyTrendData.map(d => d.unmatched),
        itemStyle: { color: '#ef4444' }
      }
    ]
  };


  const exportToCSV = () => {
    const headers = Object.keys(filteredData[0] || {}).join(',');
    const rows = filteredData.map(row =>
      Object.values(row).map(v => `"${v}"`).join(',')
    ).join('\n');

    const csv = `${headers}\n${rows}`;
    // Add UTF-8 BOM to preserve Spanish accents
    const utf8BOM = '\uFEFF';
    const blob = new Blob([utf8BOM + csv], { type: 'text/csv;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_operaciones_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <div className="reports-container">
        <div className="loading-state">
          <p>Cargando datos del reporte...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reports-container">
      <div className="reports-header">
        <h1>Reportes de Confirmación de Operaciones</h1>
        <button className="export-button" onClick={exportToCSV}>
          Exportar a CSV
        </button>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label>Rango de Fechas</label>
          <select
            value={selectedDateRange}
            onChange={(e) => {
              setSelectedDateRange(e.target.value);
              if (e.target.value !== 'custom') {
                setStartDate('');
                setEndDate('');
              }
            }}
          >
            <option value="7">Últimos 7 días</option>
            <option value="14">Últimos 14 días</option>
            <option value="30">Últimos 30 días</option>
            <option value="0">Todo el Tiempo</option>
            <option value="custom">Personalizado</option>
          </select>
        </div>

        {selectedDateRange === 'custom' && (
          <>
            <div className="filter-group">
              <label>Fecha Desde</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Fecha Hasta</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </>
        )}

        <div className="filter-group">
          <label>Estado</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
          >
            {statuses.map(status => (
              <option key={status} value={status}>
                {status === 'All' ? 'Todos los Estados' : status}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Contraparte</label>
          <select
            value={selectedCounterparty}
            onChange={(e) => setSelectedCounterparty(e.target.value)}
          >
            {counterparties.map(cp => (
              <option key={cp} value={cp}>
                {cp === 'All' ? 'Todas las Contrapartes' : cp}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Tipo de Producto</label>
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
          >
            {products.map(product => (
              <option key={product} value={product}>
                {product === 'All' ? 'Todos los Productos' : product}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-value">{stats.total}</div>
          <div className="card-label">Total Operaciones</div>
        </div>
        <div className="summary-card success">
          <div className="card-value">{stats.fullyMatched}</div>
          <div className="card-label">Coincidencias Completas</div>
        </div>
        <div className="summary-card warning">
          <div className="card-value">{stats.unmatched}</div>
          <div className="card-label">Sin Coincidencia</div>
        </div>
        <div className="summary-card info">
          <div className="card-value">{stats.matchRate}%</div>
          <div className="card-label">Tasa de Coincidencia</div>
        </div>
        <div className="summary-card">
          <div className="card-value">{stats.confirmationEmailsSent}</div>
          <div className="card-label">Correos de Confirmación</div>
        </div>
        <div className="summary-card">
          <div className="card-value">{stats.settlementsSent}</div>
          <div className="card-label">Cartas de Instrucción</div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <ReactEcharts option={statusChartOption} style={{ height: '300px' }} />
        </div>
        <div className="chart-container wide">
          <ReactEcharts option={trendChartOption} style={{ height: '300px' }} />
        </div>
      </div>

      <div className="grid-section">
        <h2>Detalles de Operaciones</h2>
        <div className="ag-theme-alpine-dark" style={{ height: 500, width: '100%' }}>
          <AgGridReact
            rowData={filteredData}
            columnDefs={columnDefs}
            onGridReady={onGridReady}
            defaultColDef={{
              resizable: true,
              sortable: true,
              minWidth: 50
            }}
            animateRows={true}
            pagination={true}
            paginationPageSize={20}
            suppressHorizontalScroll={false}
          />
        </div>
      </div>

    </div>
  );
};

export default Reports;