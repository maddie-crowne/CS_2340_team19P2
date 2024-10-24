document.addEventListener('DOMContentLoaded', function() {
    const audioElements = Array.from(document.querySelectorAll('.track-audio'));
    const playButton = document.getElementById('play-tracks');
    let currentTrackIndex = 0;

    // Function to play the current track
    function playTrack(index) {
        if (index >= audioElements.length) {
            index = 0; // Wrap around
        }
        const audio = audioElements[index];
        audio.play();

        // Listen for the 'ended' event to play the next track
        audio.onended = () => {
            playTrack(index + 1);
        };
    }

    playButton.addEventListener('click', function () {
        playTrack(currentTrackIndex);
    });
});
