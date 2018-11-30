Design document for tweetView App

# v0.1

### Workflow
- User uploads a file of tweet IDs
- File gets passed into a parser which generates the tweet widget
- tweet widget get's embedded into the HTML

### Code Blocks
- File upload handler
  - csv parsers
- twitter widget iterator
  - iterator over tweet ids to display in list
- Some sort of way to cache pages for different projects
- index.html handles the display of the tweets

### Solution
- First attempt will be to do this in a flask app
