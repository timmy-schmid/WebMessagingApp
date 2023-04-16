//Client Side RSA key generation,storage and sending
  function generateRSA(form_id) {
      if (!localStorage.RSAPublicKey || !localStorage.RSASecretKey) {
          var crypt = new JSEncrypt({default_key_size: 512});
          crypt.getKey();
          localStorage.RSAPublicKey = crypt.getPublicKey();
          localStorage.RSASecretKey = crypt.getPrivateKey();
      }

      // Create hidden form element that cotains the PK for the server to store. Note: we do not send the SK
      let form = document.getElementById(form_id);
      const hiddenField = document.createElement('input');
      hiddenField.type = 'hidden';
      hiddenField.name = 'public_key';
      hiddenField.value = localStorage.RSAPublicKey;
      form.appendChild(hiddenField);
  }