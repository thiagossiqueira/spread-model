// static/js/spread_table.js
$(document).ready(function () {
    $('#spread-table').DataTable({
        dom: 'Bfrtip',
        buttons: ['copyHtml5', 'excelHtml5', 'csvHtml5', 'pdfHtml5', 'print'],
        pageLength: 20,
        scrollX: true,
        order: [[0, 'desc']]
    });
});
