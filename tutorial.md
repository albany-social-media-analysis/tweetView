## Tutorial

If you haven't installed, set up, and started tweetView yet, follow the instructions in the [README](https://github.com/nschiraldi/tweetView/blob/master/README.md).

### Basics 

While tweetView runs on a server or VM, it expects to work with data that lives in the cloud in Google Sheets. When collecting data, the only information tweetView needs about tweets is the ID for each tweet. Using Twitter's oembed API, it renders each tweet in the browser window. It also provides a range of ways for users to label data.

#### Setting up the Google Sheets file
tweetView expects three things in a dataset living in Google Sheets:  
1) A column containing all of the IDs for the tweets in the dataset. Each ID should be prepended with "ID_" (e.g., "ID_1044977754729414656"). This should be the first column of the sheet, and it should be named "tweet_id_str".
2) A placeholder column that will contain the username of the tweetView user who labeled each tweet. This should be the second column of the sheet, and it should be named "user".  
3) A number of columns that will contain the labels for each tweet. There does not seem to be a limit to the number of columns used for this purpose. By default, tweetView will display the column name and a text box for open-ended labeling.  

When the Sheet is ready for tweetView, click "Share" in the upper right corner. Generate a shareable link, and make sure that anyone with the link can edit the sheet. 

#### Getting started on tweetView
By default, tweetView will be accessible via browser at http://{server or VM URL}:8091.  

The landing page for tweetView prompts users to login or create a login. It asks for an email address, which serves as the username; this email address does not need to be a Google account.  
After logging in, the user will see a mostly blank screen with a prompt to "Provide a Link to a Google Sheet". The user should enter the shareable link associated with the Sheet that will hold their work. 
* tweetView supports using multiple sheets in each Sheet (in Excel parlance, this would be multiple worksheets within a workbook). The default value provided in the sheet name field (between the Google Sheet link field and the "Update Drive URL button") matches the default name of the first sheet of a Sheet.  

After entering the link to the Google Sheet (and changing the sheet name, if applicable), click "Update Drive URL." At this point, tweetView should begin to render tweets in the browser. Users can label data as appropriate, then hit the "next" button to move to the next tweet. When the "next" (or "previous") button is pressed, tweetView will send the username and any labels to the Google Sheet.  
When tweetView reaches the end of a Sheet, it will show an error message reading "There are no more tweets left in the sheet!" It will not loop around to the start of the Sheet.  
If tweetView comes across a tweet that no longer exists (for example, a deleted tweet), it will display a "404 Client Error" in place of a rendered tweet. 

#### Multiple users coding the same data?
tweetView isn't set up to allow multiple users to label the same data in the same spreadsheet. Instead, you have two options:
1) Use one Sheets file with a different worksheet for each user.
2) Create a copy of the Sheets file for each different user.  

Either way, it's a good idea to save one copy of the sheet containing the tweet IDs and the columns in case you decide to add more users later.    

#### Advanced usage
By default, tweetView will allow users to input text in a text box with no limitations. This can make data cleaning and analysis more complicated.  
To simplify that stage of things, you might want users to choose between mutually exclusive options for a given label category -- and you might want users to perform this task for more than one label category.  
You can do this by using data validation in Google Sheets. To do this:
1) Create a column in the Google Sheet for the label category (aka variable). In the first row, put the label category name or prompt that you want users to respond to.  
2) Select all of the rows of that column except the first row. 
3) Click "Data" in the menu just below the file name, then click "Data validation...". One of the easiest ways to use this function is to change "Criteria" to "List of items", then provide each of the options in the box to the right. Note that you do not need to put spaces between the options in this box.  
  a) In tweetView, this will appear as the name of the label category on the left with each of the options appearing next to a radio button to the right of the label category name.  
  b) Note that users will only be able to select one of the options for each label category for each tweet. This means you need to be careful to construct the options for labels to be mutually exclusive if you want to use this feature.
4) Repeat these steps for each label category (aka variable) that you want to provide close-ended options for users to choose between.    

You can mix and match close-ended columns (using data validation) with open-ended columns (by not using data validation) as appropriate for your use case.  
