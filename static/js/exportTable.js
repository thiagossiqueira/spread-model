function exportTableToExcel() {
  const iframe = document.querySelector("iframe");
  const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
  const table = iframeDoc.querySelector("table");

  if (!table) {
    alert("Tabela não carregada ainda.");
    return;
  }

  const wb = XLSX.utils.table_to_book(table);
  XLSX.writeFile(wb, "summary_table.xlsx");
}
