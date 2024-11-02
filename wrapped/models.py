from django.db import models
from django.contrib.auth.models import User

class SaveWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Store user data and top artists as JSON
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