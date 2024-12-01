from django.db import models
from django.contrib.auth.models import User


class SaveWrap(models.Model):
    """
    Model to store the user's Spotify wrapped data, including top artists,
    tracks, genres, and other statistics.

    Attributes:
        user (ForeignKey): The user associated with this wrap.
        user_data (JSONField): A JSON field to store general user data.
        top_artists (JSONField): A JSON field to store the top artists of the user.
        artist_songs (JSONField): A dictionary to store the user's songs for each artist.
        top_tracks (JSONField): A JSON field to store the user's top tracks.
        top_genres (JSONField): A list to store the user's top genres.
        genre_songs (JSONField): A dictionary to store the user's songs for each genre.
        average_valence (FloatField): A numerical value representing the user's average valence (mood).
        time_range (CharField): A string representing the time range of the wrap (e.g., '2023', 'last 6 months').
        created_at (DateTimeField): The date and time when the wrap was created (auto-generated).

    Methods:
        __str__: Returns a string representation of the SaveWrap instance, showing the user's username and time range.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Wrapped info
    user_data = models.JSONField()  # JSON
    top_artists = models.JSONField()  # JSON
    artist_songs = models.JSONField(default=dict)  # Store as dict
    top_tracks = models.JSONField()  # JSON
    top_genres = models.JSONField(default=list)  # Store as list
    genre_songs = models.JSONField(default=dict)  # Store as dict
    average_valence = models.FloatField()  # number
    time_range = models.CharField(max_length=50)  # string

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the SaveWrap instance.

        The string includes the username of the associated user and the time range
        of the wrap (e.g., '2024', 'last 6 months').

        :return str: The string representation of the SaveWrap instance.
        """
        return f"Saved Wrap for {self.user.username} ({self.time_range})"


class SaveDuoWrap(models.Model):
    """
    Model to store the duo wrapped data for two users, including compatibility
    scores, top tracks, and other statistics.

    Attributes:
        user (ForeignKey): The user associated with this duo wrap.
        user1_data (JSONField): A JSON field to store general data for the first user.
        user2_data (JSONField): A JSON field to store general data for the second user.
        compatibility (IntegerField): A numerical score representing the compatibility between the two users.
        valence_user1 (FloatField): The valence (mood) value for the first user.
        valence_user2 (FloatField): The valence (mood) value for the second user.
        top_tracks_user1 (JSONField): A JSON field to store the top tracks for the first user.
        top_tracks_user2 (JSONField): A JSON field to store the top tracks for the second user.
        interleaved_preview_urls (JSONField): A JSON field to store preview URLs for the interleaved duo tracks.
        created_at (DateTimeField): The date and time when the duo wrap was created (auto-generated).

    Methods:
        __str__: Returns a string representation of the SaveDuoWrap instance, showing the user's username.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Duo wrapped info
    user1_data = models.JSONField()  # JSON
    user2_data = models.JSONField()  # JSON
    compatibility = models.IntegerField()  # number
    valence_user1 = models.FloatField()  # number
    valence_user2 = models.FloatField()  # number
    top_tracks_user1 = models.JSONField()  # JSON
    top_tracks_user2 = models.JSONField()  # JSON
    interleaved_preview_urls = models.JSONField()  # JSON

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the SaveDuoWrap instance.

        The string includes the username of the associated user.

        :return str: The string representation of the SaveDuoWrap instance.
        """
        return f"Saved Duo Wrap for {self.user.username}"
