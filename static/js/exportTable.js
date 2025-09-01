function exportTableToExcel(tableId, filename = 'table.xlsx') {
    const table = document.getElementById(tableId);
    if (!table) {
        alert("Tabela não carregada ainda.");
        return;
    }

    const wb = XLSX.utils.table_to_book(table, { sheet: "Resumo" });
    XLSX.writeFile(wb, filename);
}
