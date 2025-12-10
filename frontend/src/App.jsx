import { useState } from 'react';
import UploadForm from "./components/UploadForm";
import GetResults from "./components/GetResults";
import ImageModal from './components/ImageModal';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);

  return (
    <div className="container">
      <header className="mb-4 text-center">
        <h1>Image Processing Dashboard</h1>
        <p style={{ color: "var(--text-muted)" }}>Upload and process your images effortlessly</p>
      </header>

      <main>
        <UploadForm onImageClick={setSelectedImage} />
        <GetResults onImageClick={setSelectedImage} />
      </main>

      <ImageModal
        image={selectedImage}
        onClose={() => setSelectedImage(null)}
      />
    </div>
  );
}

export default App;