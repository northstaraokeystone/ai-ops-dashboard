import React from 'react';
import { useTable, useSortBy, useExpanded } from 'react-table'; // TanStack for efficient table per design_system_v1.md
import { ChevronDown, ChevronRight } from 'lucide-react'; // Icons for expand
import { useStore } from 'zustand';
import { incidentStore } from '../stores/incidentStore';

const AccountabilityTable: React.FC = () => {
  const { incidents, toggleExpand, sortBy } = useStore(incidentStore);

  const columns = React.useMemo(() => [
    {
      Header: '',
      accessor: 'expanded',
      Cell: ({ row }) => (
        <button onClick={() => toggleExpand(row.original.id)} aria-label="Toggle expand">
          {row.isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </button>
      ),
      disableSortBy: true,
    },
    { Header: 'Status', accessor: 'status' },
    { Header: 'Agent Name', accessor: 'agentName' },
    { Header: 'Action', accessor: 'action' },
    { Header: 'Owner', accessor: 'owner' },
    { Header: 'Time', accessor: 'time' },
  ], []);

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable(
    { columns, data: incidents },
    useSortBy,
    useExpanded
  );

  return (
    <table {...getTableProps()} className="w-full border-collapse" aria-label="Accountability Table">
      <thead>
        {headerGroups.map((headerGroup) => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map((column) => (
              <th {...column.getHeaderProps(column.getSortByToggleProps())} className="p-2 text-left font-semibold">
                {column.render('Header')}
                {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row);
          return (
            <React.Fragment key={row.id}>
              <tr {...row.getRowProps()} className="border-t">
                {row.cells.map((cell) => (
                  <td {...cell.getCellProps()} className="p-2">{cell.render('Cell')}</td>
                ))}
              </tr>
              {row.isExpanded && (
                <tr>
                  <td colSpan={columns.length} className="p-2 bg-gray-100">
                    <pre aria-label="Raw payload" className="overflow-auto">{JSON.stringify(row.original.agentSupport, null, 2)}</pre>
                  </td>
                </tr>
              )}
            </React.Fragment>
          );
        })}
      </tbody>
    </table>
  );
};

export default AccountabilityTable;
