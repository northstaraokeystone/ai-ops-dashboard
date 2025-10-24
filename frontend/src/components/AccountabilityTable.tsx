import React from 'react';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useStore } from 'zustand';
import { incidentStore, Incident } from '../stores/incidentStore'; // Assuming Incident type is exported

const columnHelper = createColumnHelper<Incident>();

const columns = [
  columnHelper.accessor('expanded', {
    header: '',
    cell: ({ row }) => (
      <button onClick={() => row.toggleExpanded()} aria-label="Toggle expand">
        {row.getIsExpanded() ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
    ),
    enableSorting: false,
  }),
  columnHelper.accessor('status', {
    header: 'Status',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('agentName', {
    header: 'Agent Name',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('action', {
    header: 'Action',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('owner', {
    header: 'Owner',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('time', {
    header: 'Time',
    cell: info => info.getValue(),
  }),
];

const AccountabilityTable: React.FC = () => {
  const { incidents, toggleExpand } = useStore(incidentStore);

  const table = useReactTable({
    data: incidents,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getExpandedRowModel: getCoreRowModel(), // Or a more specific one if needed
    getRowCanExpand: () => true,
  });

  return (
    <table className="w-full border-collapse" aria-label="Accountability Table">
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id} colSpan={header.colSpan} className="p-2 text-left font-semibold">
                {header.isPlaceholder ? null : (
                  <div
                    {...{
                      className: header.column.getCanSort()
                        ? 'cursor-pointer select-none'
                        : '',
                      onClick: header.column.getToggleSortingHandler(),
                    }}
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                    {{
                      asc: ' ↑',
                      desc: ' ↓',
                    }[header.column.getIsSorted() as string] ?? null}
                  </div>
                )}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <React.Fragment key={row.id}>
            <tr className="border-t">
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="p-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
            {row.getIsExpanded() && (
              <tr>
                <td colSpan={row.getVisibleCells().length} className="p-2 bg-gray-800">
                  <pre aria-label="Raw payload" className="overflow-auto text-white">{JSON.stringify(row.original.agentSupport, null, 2)}</pre>
                </td>
              </tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
};

export default AccountabilityTable;
