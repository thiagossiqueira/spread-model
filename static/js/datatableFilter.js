document.addEventListener("DOMContentLoaded", function () {
  let table = $("#summary-table").DataTable({
    orderCellsTop: true,
    fixedHeader: true,
    dom: "Bfrtip",
    buttons: ["excel"],
  });

  // Adiciona campo de busca para cada coluna
  $("#summary-table thead tr")
    .clone(true)
    .appendTo("#summary-table thead");
  $("#summary-table thead tr:eq(1) th").each(function (i) {
    var title = $(this).text();
    $(this).html('<input type="text" placeholder="Filtrar ' + title + '" />');

    $("input", this).on("keyup change", function () {
      if (table.column(i).search() !== this.value) {
        table.column(i).search(this.value).draw();
      }
    });
  });
});
