class Animation():
   """Class to provide tile animation"""
   
   def __init__(self, frames):
      """
      Setup the animation, not playing yet.

      frames - list of tile indexes to iterate through when played.
      """

      #store the frame list
      self.frames = frames

      #set variables
      self.loop = False
      self.current = 0
      self.active = False

   def play(self, loop, start=0):
      """
      Start the animation playing.

      loop - whether or not to loop the animation at the end.
      start - the frame to start at.
      """

      #set the animation up and set it active
      self.loop = loop
      self.current = start
      self.active = True

   def getFrame(self):
      """Gets the current frame of the animation"""

      #return the required frame
      return self.frames[self.current]

   def tick(self, i=1):
      """
      Advance the animation.

      i - the number of frames to advance.
      """

      #advance the animation, then check whether we've reached the end
      #if so, go back to the start, and if we're not looping set inactive
      self.current += i
      if self.current >= len(self.frames):
         self.current = 0
         if not self.loop:
            self.active = False
