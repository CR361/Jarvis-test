/**
 * AUTOMATISCH GEGENEREERD - VOOR GEBRUIK MET VERCEL/NODE.JS
 * Handmatige aanpassingen kunnen nodig zijn voor optimale functionaliteit.
 * Dit is een automatische vertaling van Python code naar JavaScript/Node.js.
 * Deze module bevat alle contractsjablonen in JSON formaat.
 * 
 * Originele Python bestandsnaam: contract_templates.py
 * Geconverteerd op: 10-04-2025 21:37:35
 */

/**
 * Beschikbare contractsjablonen
 * @type {Array}
 */
const templates = [
];

/**
 * Retourneert een lijst van beschikbare contractsjablonen voor gebruik in de applicatie.
 * @returns {Array} Een lijst van sjabloongegevens
 */
function getContractTemplates() {
    return templates;
}

// Export de templates voor Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getContractTemplates,
    templates
  };
}

// Browser exports
if (typeof window !== 'undefined') {
  window.ContractTemplates = {
    getContractTemplates,
    templates
  };
}