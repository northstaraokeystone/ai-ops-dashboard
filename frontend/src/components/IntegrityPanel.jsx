import React, { useState } from 'react';

/**
 * IntegrityPanel component: Displays a list of interactions in an expandable table.
 *
 * Why: Enhances basic table with stateful expansion for details, using hooks for reactivity
 * and conditional render for performance (only show JSON when expanded). Handles empty state
 * for UX resilience; map with keys for efficient list reconciliation. Aligns with React
 * functional patterns and Fowler refactoring for evolvable trust fabric UIs, maintaining
 * SRP: focused on display/expansion without data fetching.
 *
 * @param {Object} props - Component props
 * @param {Array<Object>} props.interactions - Array of interaction objects with id, agent_id, action_type, emitted_at_utc, agent_support
 * @returns {JSX.Element} The rendered table or empty message
 */
const IntegrityPanel = ({ interactions }) => {
  // State for tracking expanded row
  // Why: Single id limits to one expansion for simplicity/focus, null initial for collapsed start;
  // useState for local reactivity, aligning with React hooks for minimal global state.
  const [expandedRowId, setExpandedRowId] = useState(null);

  // Conditional render for empty state
  // Why: Prevents rendering empty table for better UX, avoiding visual clutter and aligning
  // with Pragmatic Programmer user-centric design; simple if for minimal logic.
  if (interactions.length === 0) {
    return <p>No interactions found.</p>;
  }

  return (
    <table className="table-auto w-full border-collapse border border-gray-300">
      <thead className="bg-gray-200">
        <tr>
          <th className="border px-4 py-2 text-left">ID</th>
          <th className="border px-4 py-2 text-left">Agent ID</th>
          <th className="border px-4 py-2 text-left">Action Type</th>
          <th className="border px-4 py-2 text-left">Timestamp</th>
          <th className="border px-4 py-2 text-left">Details</th> {/* New column for button */}
        </tr>
      </thead>
      <tbody>
        {interactions.map((interaction) => (
          <React.Fragment key={interaction.id}>
            {/* Main data row */}
            <tr>
              <td className="border px-4 py-2">{interaction.id}</td>
              <td className="border px-4 py-2">{interaction.agent_id}</td>
              <td className="border px-4 py-2">{interaction.action_type}</td>
              <td className="border px-4 py-2">{interaction.emitted_at_utc}</td>
              <td className="border px-4 py-2">
                {/* Expand button with toggle */}
                {/* Why: onClick toggles state (set to id or null), providing accordion-like UX;
                * simple conditional text for visual feedback, maintaining accessibility. */}
                <button
                  onClick={() => setExpandedRowId(expandedRowId === interaction.id ? null : interaction.id)}
                  className="px-2 py-1 bg-blue-500 text-white rounded"
                >
                  {expandedRowId === interaction.id ? 'Collapse' : 'Expand'}
                </button>
              </td>
            </tr>
            {/* Conditional expandable row */}
            {expandedRowId === interaction.id && (
              <tr>
                {/* Details td spanning all columns */}
                {/* Why: colSpan=5 matches header count; pre with stringify for formatted JSON,
                * enabling interpretability without custom parsers, aligning with trust fabric transparency. */}
                <td colSpan="5" className="border px-4 py-2 bg-gray-100">
                  <pre>{JSON.stringify(interaction.agent_support, null, 2)}</pre>
                </td>
              </tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
};

export default IntegrityPanel;
