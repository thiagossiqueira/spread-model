// static/js/export.js

function exportToExcel(iframeId = "summary-frame", filename = "summary_export.xls") {
  const iframe = document.getElementById(iframeId);
  if (!iframe || !iframe.contentDocument) {
    alert("Iframe not found or not accessible.");
    return;
  }

  const table = iframe.contentDocument.querySelector("table");
  if (!table) {
    alert("Tabela não carregada ainda.");
    return;
  }

  const tableHtml = table.outerHTML.replace(/ /g, '%20');

  const downloadLink = document.createElement("a");
  document.body.appendChild(downloadLink);
  downloadLink.href = 'data:application/vnd.ms-excel,' + tableHtml;
  downloadLink.download = filename;
  downloadLink.click();
  document.body.removeChild(downloadLink);
}
