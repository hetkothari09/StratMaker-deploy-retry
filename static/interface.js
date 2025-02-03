
document.addEventListener('DOMContentLoaded', function() {
      const zoomButtons = document.querySelectorAll('.zoom-btn');
      const closeButtons = document.querySelectorAll('.close-btn');

      zoomButtons.forEach(button => {
        button.addEventListener('click', function() {
          const zoomedContent = this.closest('.chat-entry').querySelector('.zoomed-content');
          zoomedContent.style.display = 'block';
        });
      });

      closeButtons.forEach(button => {
        button.addEventListener('click', function() {
          const zoomedContent = this.closest('.zoomed-content');
          zoomedContent.style.display = 'none';
        });
      });

      const downloadBtn = document.getElementById('downloadJson');
      if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
          const result = document.getElementById('result').textContent;
          const fileName = prompt("Enter the file name", "response");
          if (fileName) {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ result: result }));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", fileName + ".json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
          }
        });
      }

      const modeToggle = document.getElementById('modeToggle');
      const body = document.body;
      const navbar = document.querySelector('.navbar');

      function setMode(mode) {
        if (mode === 'light') {
          body.classList.add('light-mode');
          body.classList.remove('dark-mode');
          navbar.classList.add('navbar-light-mode');
          navbar.classList.remove('navbar-dark-mode');
          modeToggle.textContent = 'Dark Mode';
        } else {
          body.classList.add('dark-mode');
          body.classList.remove('light-mode');
          navbar.classList.add('navbar-dark-mode');
          navbar.classList.remove('navbar-light-mode');
          modeToggle.textContent = 'Light Mode';
        }
      }

      modeToggle.addEventListener('click', function() {
        const currentMode = body.classList.contains('dark-mode') ? 'dark' : 'light';
        const newMode = currentMode === 'dark' ? 'light' : 'dark';
        setMode(newMode);
        localStorage.setItem('mode', newMode);
      });

      const savedMode = localStorage.getItem('mode');
      if (savedMode) {
        setMode(savedMode);
      } else {
        const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        setMode(prefersDarkMode ? 'dark' : 'light');
      }
    });


      let recognition = null;
      let isListening = false;

      function toggleSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
          alert("Speech recognition is not supported in this browser.");
          return;
        }

        if (!isListening) {
          startListening();
        } else {
          stopListening();
        }
      }

      function startListening() {
        recognition = new webkitSpeechRecognition();
        recognition.lang = "en-US";

        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function(event) {
          let resultText = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              resultText += event.results[i][0].transcript;
            }
          }
          const textarea = document.getElementById('prompt_data');
          textarea.value += resultText;
        };

        recognition.onerror = function(event) {
          console.error("Speech recognition error", event.error);
        };

        recognition.onend = function() {
          console.log("Speech recognition service disconnected");
          isListening = false;
        };

        recognition.start();
        isListening = true;
      }

      function stopListening() {
        if (recognition) {
          recognition.stop();
          isListening = false;
        }
      }


    function showZoomedContent() {
      const zoomedContent = document.querySelector('.zoomed-content');
      const overlay = document.createElement('div');
      overlay.className = 'overlay';
      document.body.appendChild(overlay);
      overlay.classList.add('show');
      zoomedContent.classList.add('show');

      overlay.addEventListener('click', function() {
        zoomedContent.classList.remove('show');
        overlay.classList.remove('show');
        document.body.removeChild(overlay);
      });
}


