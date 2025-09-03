/**
 * Central Bank Trade Codes (Códigos de Comercio BCCh)
 * Source: A.10 Códigos Conceptos de Ingresos y Egresos A.T. 2008 Asociados al Formulario 1862
 */

export interface TradeCode {
  code: string;
  concept: string;
  type: 'income' | 'expense';
}

export const CENTRAL_BANK_TRADE_CODES: TradeCode[] = [
  // INCOME CODES (INGRESOS)
  { code: '10000', concept: 'Servicios de Comunicación, Construcción y Transporte.', type: 'income' },
  { code: '10002', concept: 'Servicios de Informática.', type: 'income' },
  { code: '10005', concept: 'Servicios Empresariales, Profesionales, Honorarios y Técnicos varios.', type: 'income' },
  { code: '10007', concept: 'Servicios Personales, Culturales y Recreativos.', type: 'income' },
  { code: '10008', concept: 'Servicios de Información.', type: 'income' },
  { code: '10020', concept: 'Créditos Internos en moneda extranjera para Financiamiento de Exportaciones.', type: 'income' },
  { code: '10024', concept: 'Jubilaciones, Montepíos, Ayudas Familiares y otras Donaciones.', type: 'income' },
  { code: '10025', concept: 'Otros Créditos Internos en moneda extranjera.', type: 'income' },
  { code: '10028', concept: 'Representaciones Diplomáticas, Misiones, Organismos Internacionales y otras Oficinas de Representación.', type: 'income' },
  { code: '10040', concept: 'Arrendamiento de Equipo de Transporte y Maquinaria.', type: 'income' },
  { code: '10050', concept: 'Ingresos de Agencias de Valores, Corredoras de Bolsa, Bancos de Inversión otros similares.', type: 'income' },
  { code: '10051', concept: 'Compras al Banco Central de Chile.', type: 'income' },
  { code: '10052', concept: 'Compras a Empresas Bancarias.', type: 'income' },
  { code: '10053', concept: 'Compras a Personas Jurídicas autorizadas conforme al Capítulo III del Compendio.', type: 'income' },
  { code: '10055', concept: 'Compras por Arbitraje de Divisas', type: 'income' },
  { code: '10057', concept: 'Compras a la Tesorería General de la República', type: 'income' },
  { code: '10060', concept: 'Ingresos por liquidación de Cuentas de Resultado, de Reservas y de Provisiones en moneda extranjera.', type: 'income' },
  { code: '10070', concept: 'Ingresos por Turismo', type: 'income' },
  { code: '10075', concept: 'Liquidación de Depósitos en moneda extranjera', type: 'income' },
  { code: '10080', concept: 'Ingresos no contemplados en otros Códigos de Operaciones de Cambios.', type: 'income' },
  { code: '10090', concept: 'Divisas informadas previamente.', type: 'income' },
  { code: '10400', concept: 'Retornos de Exportaciones.', type: 'income' },
  { code: '10425', concept: 'Ingresos de Corresponsal por operaciones con el exterior.', type: 'income' },
  { code: '10450', concept: 'Anticipos de Comprador.', type: 'income' },
  { code: '10460', concept: 'CODELCO.', type: 'income' },
  { code: '10480', concept: 'Ingresos por intermediación y por otras actividades de comercio exterior.', type: 'income' },
  { code: '10570', concept: 'Comisiones por actividades de Comercio Exterior.', type: 'income' },
  { code: '10700', concept: 'Primas de Seguros, Reaseguros, y otros ingresos asociados.', type: 'income' },
  { code: '10750', concept: 'Indemnizaciones por/sin Contratos de Seguros.', type: 'income' },
  { code: '10822', concept: 'Aportes, Empréstitos y Donaciones a Corporaciones y otras personas jurídicas sin fines de lucro (D.L. N° 1.183 de 1975).', type: 'income' },
  { code: '10830', concept: 'Regalías, Derechos de Autor y de Licencia por uso de marcas y patentes.', type: 'income' },
  { code: '10900', concept: 'Ingresos por operaciones con Instrumentos Derivados pactadas con residentes en el exterior.', type: 'income' },
  { code: '10950', concept: 'Ingresos por operaciones con Instrumentos Derivados pactadas en el mercado local con Entidades M.C.F.', type: 'income' },
  { code: '11025', concept: 'Ingresos por Garantías, Avales, Fianzas y otros similares.', type: 'income' },
  { code: '11100', concept: 'Fondos de Inversión de Capital Extranjero', type: 'income' },
  { code: '11200', concept: 'Retorno de capital de Derechos o Acciones de Empresas o Sociedades.', type: 'income' },
  { code: '11201', concept: 'Retorno de utilidades de Derechos o Acciones de Empresas o Sociedades.', type: 'income' },
  { code: '11220', concept: 'Retorno de capital de Bonos y Pagarés adquiridos en el exterior.', type: 'income' },
  { code: '11221', concept: 'Retorno de intereses de Bonos y Pagarés adquiridos en el exterior.', type: 'income' },
  { code: '11230', concept: 'Retorno de capital de inversiones en el exterior en Instrumentos de Renta Fija de corto plazo.', type: 'income' },
  { code: '11231', concept: 'Retorno de intereses de inversiones en el exterior en Instrumentos de Renta Fija de corto plazo.', type: 'income' },
  { code: '11240', concept: 'Amortización de Créditos otorgados al exterior.', type: 'income' },
  { code: '11241', concept: 'Intereses de Créditos otorgados al exterior.', type: 'income' },
  { code: '11242', concept: 'Comisiones de Créditos otorgados al exterior.', type: 'income' },
  { code: '11250', concept: 'Retorno de Depósitos constituidos en el exterior.', type: 'income' },
  { code: '11251', concept: 'Intereses de Depósitos constituidos en el exterior.', type: 'income' },
  { code: '11260', concept: 'Retorno de capital de Inversiones en el exterior en otros Activos Financieros.', type: 'income' },
  { code: '11261', concept: 'Retorno de utilidades de Inversiones en el exterior en otros Activos Financieros.', type: 'income' },
  { code: '11270', concept: 'Retorno de capital de Inversiones en el exterior en otros Activos no Financieros.', type: 'income' },
  { code: '11271', concept: 'Retorno de utilidades de Inversiones en el Exterior en otros Activos no Financieros.', type: 'income' },
  { code: '11280', concept: 'Ingresos por inversiones en Valores Extranjeros o C.D.V.', type: 'income' },
  { code: '11400', concept: 'Créditos Externos.', type: 'income' },
  { code: '11405', concept: 'Créditos Externos asociados al D.L. 600.', type: 'income' },
  { code: '11410', concept: 'Bonos emitidos y colocados en el exterior.', type: 'income' },
  { code: '11415', concept: 'Ingresos por venta de Créditos Externos.', type: 'income' },
  { code: '11420', concept: 'Depósitos del exterior.', type: 'income' },
  { code: '11450', concept: 'Aportes de Capital para constituir o aumentar el capital de personas jurídicas residentes en Chile.', type: 'income' },
  { code: '11470', concept: 'Inversiones para adquirir Acciones o Derechos de Sociedades.', type: 'income' },
  { code: '11475', concept: 'Inversiones del exterior en Bienes Raíces o Bienes Muebles.', type: 'income' },
  { code: '11480', concept: 'Inversiones del exterior en Bonos, Pagarés y otros Valores domésticos.', type: 'income' },
  { code: '11485', concept: 'Inversión Extranjera amparada por el D.L. 600', type: 'income' },
  { code: '11490', concept: 'Ingresos para compra de Acciones de S.A. o de Cuotas de Fondos de Inversión.', type: 'income' },
  { code: '11495', concept: 'Comisiones, Corretaje, Custodia, Honorarios y otros ingresos por inversiones en el exterior.', type: 'income' },

  // EXPENSE CODES (EGRESOS)
  { code: '20000', concept: 'Servicios de Comunicación, Construcción y Transporte.', type: 'expense' },
  { code: '20002', concept: 'Servicios de Informática.', type: 'expense' },
  { code: '20005', concept: 'Servicios Empresariales, Profesionales, Honorarios y Técnicos varios.', type: 'expense' },
  { code: '20007', concept: 'Servicios Personales, Culturales y Recreativos.', type: 'expense' },
  { code: '20008', concept: 'Servicios de Información.', type: 'expense' },
  { code: '20020', concept: 'Amortización de Créditos Internos en moneda extranjera para Financiamiento de Exportaciones.', type: 'expense' },
  { code: '20021', concept: 'Intereses de Créditos Internos en moneda extranjera para Financiamiento de Exportaciones.', type: 'expense' },
  { code: '20023', concept: 'Aportes y Cuotas a Organismos Internacionales.', type: 'expense' },
  { code: '20024', concept: 'Jubilaciones, Montepíos, Ayudas Familiares y Donaciones.', type: 'expense' },
  { code: '20025', concept: 'Amortización de otros Créditos Internos en moneda extranjera.', type: 'expense' },
  { code: '20026', concept: 'Intereses de otros Créditos Internos en moneda extranjera.', type: 'expense' },
  { code: '20028', concept: 'Representaciones Diplomáticas, Misiones y otras Oficinas de Representación en el exterior.', type: 'expense' },
  { code: '20040', concept: 'Arrendamiento de Equipo de Transporte y Maquinaria.', type: 'expense' },
  { code: '20050', concept: 'Egresos de Agencias de Valores, Corredoras y otras similares.', type: 'expense' },
  { code: '20051', concept: 'Ventas al Banco Central de Chile.', type: 'expense' },
  { code: '20052', concept: 'Ventas a Empresas Bancarias.', type: 'expense' },
  { code: '20053', concept: 'Ventas a Personas Jurídicas autorizadas conforme al Capítulo III del Compendio.', type: 'expense' },
  { code: '20055', concept: 'Ventas por Arbitrajes de Divisas.', type: 'expense' },
  { code: '20057', concept: 'Ventas a la Tesorería General de la República.', type: 'expense' },
  { code: '20080', concept: 'Liquidación Reservas / Turismo / Otros Egresos no contemplados', type: 'expense' },
  { code: '20085', concept: 'Recuperación de liquidación Depósitos en moneda extranjera.', type: 'expense' },
  { code: '20087', concept: 'Impuestos en moneda extranjera.', type: 'expense' },
  { code: '20090', concept: 'Venta de Divisas para futuras Transferencias.', type: 'expense' },
  { code: '20420', concept: 'Adquisición de mercadería extranjera para ser procesada en Almacén Particular de Exportación.', type: 'expense' },
  { code: '20450', concept: 'Devolución de Anticipo de Comprador.', type: 'expense' },
  { code: '20470', concept: 'Comisiones y otros servicios por actividades de Comercio Exterior.', type: 'expense' },
  { code: '20500', concept: 'Coberturas de Importaciones.', type: 'expense' },
  { code: '20525', concept: 'Gastos de Corresponsal por operaciones con el exterior.', type: 'expense' }
];

// Helper function to get formatted options for dropdown
export const getTradeCodeOptions = () => {
  return CENTRAL_BANK_TRADE_CODES.map(code => ({
    value: code.code,
    label: `${code.code} - ${code.concept}`,
    type: code.type
  }));
};

// Helper function to get inflow (income) trade code options
export const getInflowTradeCodeOptions = () => {
  return CENTRAL_BANK_TRADE_CODES
    .filter(code => code.type === 'income')
    .map(code => ({
      value: code.code,
      label: `${code.code} - ${code.concept}`,
      type: code.type
    }));
};

// Helper function to get outflow (expense) trade code options
export const getOutflowTradeCodeOptions = () => {
  return CENTRAL_BANK_TRADE_CODES
    .filter(code => code.type === 'expense')
    .map(code => ({
      value: code.code,
      label: `${code.code} - ${code.concept}`,
      type: code.type
    }));
};

// Helper function to get trade code by code
export const getTradeCodeByCod = (code: string): TradeCode | undefined => {
  return CENTRAL_BANK_TRADE_CODES.find(tc => tc.code === code);
};