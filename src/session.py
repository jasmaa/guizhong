class Session:
    def __init__(self, vc):
        self.vc = vc
        self.queue = []
        self.play_music_task = None
