function exportTableToExcel(tableID, filename = 'ResumoSpreads.xlsx') {
  const table = document.getElementById(tableID);
  if (!table) return alert("Tabela não carregada ainda.");

  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.table_to_sheet(table);
  XLSX.utils.book_append_sheet(wb, ws, 'Resumo');
  XLSX.writeFile(wb, filename);
}

$(document).ready(function () {
  $('#summaryTable thead tr').clone(true).appendTo('#summaryTable thead');
  $('#summaryTable thead tr:eq(1) th').each(function (i) {
    const title = $(this).text();
    $(this).html('<input type="text" placeholder="🔍 ' + title + '" />');

    $('input', this).on('keyup change', function () {
      if (table.column(i).search() !== this.value) {
        table.column(i).search(this.value).draw();
      }
    });
  });

  const table = $('#summaryTable').DataTable({
    orderCellsTop: true,
    fixedHeader: true,
    scrollX: true,
    pageLength: 50
  });
});
