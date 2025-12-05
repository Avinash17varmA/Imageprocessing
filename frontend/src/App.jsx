import UploadForm from "./components/UploadForm";
import GetResults from "./components/GetResults";

function App() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>Image Processing Dashboard</h1>

      <UploadForm />
      <hr />
      <GetResults />
    </div>
  );
}

export default App;