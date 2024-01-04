import "./src/styles.css";
import React from "react";
import { createRoot } from "react-dom/client";
import MDEditor from "@uiw/react-md-editor";
import { useDebounce } from 'usehooks-ts'

export default function App() {
  const [value, setValue] = React.useState("**Hello world!!!**");
  const debouncedValue = useDebounce(value, 500)

  function GetGhostText(text) {
    // Call out the the API to get the ghost text
    return fetch("/ghost", {
      mode: 'cors',
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ "text": text}),
    }).then((response) => {
      return response.json();
    }).catch((error) => {
      console.log(error);
    });
  }

  React.useEffect(() => {
    // Do fetch here...
    // Triggers when "debouncedValue" changes
    UpdateText(debouncedValue);
  }, [debouncedValue])



  function UpdateText(text) {
    GetGhostText(text).then((possibility) => {
        console.log(possibility.body);
    });
  }

  return (
    <div className="container">
      <MDEditor value={value} onChange={setValue} />
      <MDEditor.Markdown source={value} style={{ whiteSpace: "pre-wrap" }} />
    </div>
  );
}

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);
