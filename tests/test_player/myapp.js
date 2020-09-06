// IMPORTANT!
// Here you should change and put the packaged video URL
// which you receive after posting json
// check documentation, you should open the port before by
// doing GET http://0.0.0.0/videos/
const manifestUri =
    'http://localhost:8080/NZ7KLC/dash/stream.mpd';

function initApp() {
  // Install built-in polyfills to patch browser incompatibilities.
  shaka.polyfill.installAll();

  // Check to see if the browser supports the basic APIs Shaka needs.
  if (shaka.Player.isBrowserSupported()) {
    // Everything looks good!
    initPlayer();
  } else {
    // This browser does not have the minimum set of APIs we need.
    console.error('Browser not supported!');
  }
}

async function initPlayer() {
  // Create a Player instance.
  const video = document.getElementById('video');
  const player = new shaka.Player(video);

  // IMPORTANT!
  // Here we add the concrete KID and KEY we need to decrypt the video.
  player.configure({
  drm: {
    clearKeys: {
      // 'key-id-in-hex': 'key-in-hex',
      'a16e402b9056e371f36d348aa62bb749': '87237d20a19f58a740c05684e699b4aa'
      }
    }
  });

  // Attach player to the window to make it easy to access in the JS console.
  window.player = player;

  // Listen for error events.
  player.addEventListener('error', onErrorEvent);

  // Try to load a manifest.
  // This is an asynchronous process.
  try {
    await player.load(manifestUri);
    // This runs if the asynchronous load is successful.
    console.log('The video has now been loaded!');
  } catch (e) {
    // onError is executed if the asynchronous load fails.
    onError(e);
  }
}

function onErrorEvent(event) {
  // Extract the shaka.util.Error object from the event.
  onError(event.detail);
}

function onError(error) {
  // Log the error.
  console.error('Error code', error.code, 'object', error);
}

document.addEventListener('DOMContentLoaded', initApp);

