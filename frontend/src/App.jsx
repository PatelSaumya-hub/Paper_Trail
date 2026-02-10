import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");

  return (
    <div style={{ padding: "20px" }}>
      <h1>📄 Paper Trail</h1>

      <input
        type="text"
        placeholder="Search research papers..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{ padding: "8px", width: "300px" }}
      />

      <button
        onClick={() => alert(query)}
        style={{ marginLeft: "10px", padding: "8px 12px" }}
      >
        Search
      </button>
    </div>
  );
}

export default App;
