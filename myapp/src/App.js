import * as React from 'react';
import { storage } from './firebase-config';
import { ref, getDownloadURL } from "firebase/storage";
import { trackPromise, usePromiseTracker } from 'react-promise-tracker'
import { RotatingLines } from 'react-loader-spinner'
import Particule from './Particule';
import './App.css';

function App() {

    const [image, setImage] = React.useState(null);
    const [imageoutput, setImageOutput] = React.useState(null)
    const inputRef = React.useRef(null);
  
    const handleChange = (e) => {
      setImage(e.target.files[0]);
    };

    // reset
    const handleReset = () => {
      setImage(null);
      setImageOutput(null)
      inputRef.current.value = "";
    };

    const handleSubmit = async () => {
      const formData = new FormData();
      formData.append("image", image);

      // envoie de l'image au back pour traitement
      try {
          const response = await trackPromise(fetch("/api/importationimage", {
              method: "POST",
              body: formData
          }));

          if (!response.ok) {
              throw new Error("Echec de l'upload de l'image");
          }
          
          // download de l'image sauvegarder dans le bucket
          getImage(image.name)
      } catch (error) {
          console.error(error);
      }
    };

    // fonction pour recuperer l'image sur google cloud storage
    const getImage = async (filename) => {
      await getDownloadURL(ref(storage, filename))
      .then((url) => {
        setImageOutput(url);
        // suppression de la reference de l'image initiale'
        setImage(null);
        inputRef.current.value = "";
      })
      .catch((error) => {
        console.log(error)
      });
    }

    const LoadingIndicator = props => {
      
      // suivi de la promess pour le chargeur
      const { promiseInProgress } = usePromiseTracker();
    
      return (
        promiseInProgress &&
        <div style={{display: "flex", justifyContent: "center", alignItems: "center", width:'80%', zIndex:'1'}}>
          <p style={{color:'snow', marginRight:"5%"}}>
            Veuillez patienter pendant le traitement...
          </p>
          <RotatingLines
            strokeColor="orangered"
            strokeWidth="5"
            animationDuration="0.75"
            width="30"
            visible={true}
          />
        </div>
      );  
    };

  return (
    <div className="App">
      <Particule/>
      <header className="App-header">
        <h2 style={{zIndex:'1'}}>
          Detection du port du masque
        </h2>
        {imageoutput === null ?
        <p style={{zIndex:'1'}}>
          Importer une image
        </p>
        : null}
        <div style={{display:'flex', justifyContent:'center', width:'80%', zIndex:'1'}}>
          {imageoutput === null ?
          <div>
            <input type="file" accept="image/jpeg, image/png" ref={inputRef} onChange={handleChange} />
            <button onClick={handleSubmit} style={{backgroundColor:'palegreen', color:'black', padding:'5px 10px 5px 10px'}}>Detecter</button>
          </div>
          : null}
          <div>
            <button onClick={handleReset} style={{backgroundColor:'crimson', color:'snow', padding:'5px 10px 5px 10px'}}>Reinitialiser</button>
          </div>
        </div>
        <LoadingIndicator/>
        <div style={{zIndex:'1'}}>
          {image && <img src={URL.createObjectURL(image)} alt="Uploaded Image" />}
        </div>
        {imageoutput !== null ?
        <div style={{zIndex:'1'}}>
          <p style={{color:'snow', textAlign:'center'}}>
            Voici le resultat de la detection
          </p>
          {imageoutput && <img src={imageoutput} alt="Output Image" />}
        </div>
        : null}
      </header>
    </div>
  );
}

export default App;
