from django.db import models
from django.contrib.auth.models import User


class SaveWrap(models.Model):
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
        return f"Saved Wrap for {self.user.username} ({self.time_range})"


class SaveDuoWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Duo wrapped info
    user1_data = models.JSONField()  # JSON
    user2_data = models.JSONField()  # JSON
    compatibility = models.FloatField()  # number
    valence_user1 = models.FloatField()  # number
    valence_user2 = models.FloatField()  # number
    top_tracks_user1 = models.JSONField()  # JSON
    top_tracks_user2 = models.JSONField()  # JSON
    interleaved_preview_urls = models.JSONField()  # JSON

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Saved Duo Wrap for {self.user.username} ({self.time_range})"
