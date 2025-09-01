$(document).ready(function () {
    $('#summaryTable thead tr').clone(true).appendTo('#summaryTable thead');
    $('#summaryTable thead tr:eq(1) th').each(function (i) {
        const title = $(this).text();
        $(this).html('<input type="text" placeholder="Search ' + title + '" />');

        $('input', this).on('keyup change', function () {
            if (table.column(i).search() !== this.value) {
                table
                    .column(i)
                    .search(this.value)
                    .draw();
            }
        });
    });

    window.table = $('#summaryTable').DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        scrollX: true,
        pageLength: 50
    });
});
