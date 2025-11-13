let currentPrediction = null;

async function predictStop() {
  const location = document.getElementById("demoLocation").value;
  const loading = document.getElementById("loading");
  const predictionCard = document.getElementById("predictionCard");
  const locationInfo = document.getElementById("locationInfo");
  const predictBtn = document.getElementById("predictBtn");
  const errorMessage = document.getElementById("errorMessage");

  // Hide previous results and errors
  errorMessage.style.display = "none";
  loading.classList.add("active");
  predictionCard.classList.remove("active");
  locationInfo.style.display = "none";
  predictBtn.disabled = true;

  try {
    const response = await fetch("http://localhost:5000/predict_from_demo", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        location: location,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Update location info
    const nearestStop = data.current_location.nearest_stop;
    document.getElementById("nearestStopInfo").innerHTML = `<strong>${
      nearestStop.english_name
    }</strong><br>
             Distance: ${nearestStop.distance_meters.toFixed(0)} meters away`;
    locationInfo.style.display = "block";

    // Update prediction
    document.getElementById("englishStop").textContent =
      data.prediction.stop_name_english;
    document.getElementById("hindiStop").textContent =
      data.prediction.stop_name_hindi;
    document.getElementById("confidence").textContent = `Confidence: ${(
      data.prediction.confidence * 100
    ).toFixed(1)}%`;

    // Store current prediction for audio
    currentPrediction = data;

    // Hide loading, show results
    loading.classList.remove("active");
    predictionCard.classList.add("active");

    // Auto-play both announcements
    if (data.play_audio) {
      setTimeout(() => playBothAnnouncements(), 1000);
    }
  } catch (error) {
    console.error("Prediction error:", error);
    showError(
      "Error predicting next stop. Please make sure the API server is running on port 5000."
    );

    // Hide loading, enable button
    loading.classList.remove("active");
    predictionCard.classList.remove("active");
    locationInfo.style.display = "none";
  } finally {
    predictBtn.disabled = false;
  }
}

async function predictFromCurrentLocation() {
  const loading = document.getElementById("loading");
  const predictionCard = document.getElementById("predictionCard");
  const locationInfo = document.getElementById("locationInfo");
  const locationStatus = document.getElementById("locationStatus");
  const currentLocationBtn = document.getElementById("currentLocationBtn");
  const errorMessage = document.getElementById("errorMessage");

  // Hide previous results and errors
  errorMessage.style.display = "none";
  loading.classList.add("active");
  predictionCard.classList.remove("active");
  locationInfo.style.display = "none";
  locationStatus.style.display = "none";
  currentLocationBtn.disabled = true;
  currentLocationBtn.innerHTML = "📍 Getting Location...";

  try {
    // Get current position
    const position = await getCurrentPosition();
    const { latitude, longitude } = position.coords;

    // Show location status
    locationStatus.innerHTML = `📍 Location found: ${latitude.toFixed(
      4
    )}, ${longitude.toFixed(4)}`;
    locationStatus.style.display = "block";

    // Send coordinates to API
    const response = await fetch(
      "http://localhost:5000/predict_from_coordinates",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude: latitude,
          longitude: longitude,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Update location info
    const nearestStop = data.current_location.nearest_stop;
    document.getElementById("nearestStopInfo").innerHTML = `<strong>${
      nearestStop.english_name
    }</strong><br>
             Distance: ${nearestStop.distance_meters.toFixed(0)} meters away`;
    locationInfo.style.display = "block";

    // Update prediction
    document.getElementById("englishStop").textContent =
      data.prediction.stop_name_english;
    document.getElementById("hindiStop").textContent =
      data.prediction.stop_name_hindi;
    document.getElementById("confidence").textContent = `Confidence: ${(
      data.prediction.confidence * 100
    ).toFixed(1)}%`;

    // Store current prediction for audio
    currentPrediction = data;

    // Hide loading, show results
    loading.classList.remove("active");
    predictionCard.classList.add("active");

    // Auto-play both announcements
    if (data.play_audio) {
      setTimeout(() => playBothAnnouncements(), 1000);
    }
  } catch (error) {
    console.error("Location/Prediction error:", error);
    if (error.code === 1) {
      showError(
        "Location access denied. Please allow location access or use demo locations."
      );
    } else if (error.code === 2) {
      showError(
        "Location unavailable. Please check your connection and try again."
      );
    } else if (error.code === 3) {
      showError("Location request timed out. Please try again.");
    } else {
      showError("Error getting location or predicting stop. Please try again.");
    }

    loading.classList.remove("active");
    predictionCard.classList.remove("active");
    locationInfo.style.display = "none";
  } finally {
    currentLocationBtn.disabled = false;
    currentLocationBtn.innerHTML = "📍 Use My Current Location";
  }
}

function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by this browser"));
    }

    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000,
    });
  });
}

function playBothAnnouncements() {
  if (!currentPrediction) return;

  // Play English first, then Hindi after a delay
  speakText(currentPrediction.audio.english, "en-US");

  // Play Hindi after English finishes (approx 3 seconds)
  setTimeout(() => {
    // Use English words for Hindi pronunciation to avoid TTS issues
    const hindiText = `Agla station hai ${currentPrediction.prediction.stop_name_english}`;
    speakText(hindiText, "en-US"); // Use English TTS for reliability
  }, 3000);
}

function playCurrentAudio() {
  if (!currentPrediction) return;
  playBothAnnouncements();
}

function speakText(text, lang = "en-US") {
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.9;
  utterance.pitch = 1;
  utterance.volume = 1;
  utterance.lang = lang;

  // Find a clear voice
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(
    (voice) =>
      voice.lang.includes("en") &&
      (voice.name.includes("Female") ||
        voice.name.includes("Google") ||
        voice.name.includes("Microsoft"))
  );

  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  utterance.onstart = () => {
    console.log("Audio announcement started:", text);
  };

  utterance.onend = () => {
    console.log("Audio announcement completed");
  };

  utterance.onerror = (event) => {
    console.error("Speech synthesis error:", event);
  };

  window.speechSynthesis.speak(utterance);
}

function showError(message) {
  const errorElement = document.getElementById("errorMessage");
  errorElement.textContent = message;
  errorElement.style.display = "block";
}

// Initialize when page loads
window.addEventListener("load", function () {
  // Load voices
  if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = () => {
      console.log("Voices loaded");
    };
  }

  console.log("Enhanced Bus Stop Predictor Ready!");
});

// Handle page visibility change
document.addEventListener("visibilitychange", function () {
  if (document.hidden && window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
  }
});
