function downloadSummaryTable() {
  const table = document.querySelector("#summary-table");
  if (!table) {
    alert("Tabela não carregada ainda.");
    return;
  }

  let wb = XLSX.utils.table_to_book(table, { sheet: "Resumo" });
  XLSX.writeFile(wb, "resumo_spread.xlsx");
}
