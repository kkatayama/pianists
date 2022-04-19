So I went ahead and added the `search` function.

After a `user` logs in, they are sent to their `dashboard`

**http://localhost:8080/dashboard**
![https://raw.githubusercontent.com/kkatayama/pianists/main/docs/dashboard.png](https://raw.githubusercontent.com/kkatayama/pianists/main/docs/dashboard.png)

The `user` can **Delete File**, **Process File**, and **Log Out** just like before.

The *new* function is **Find Sheet Music** instead of the old **Upload File**

# Find Sheet Music
**http://localhost:8080/search**
![https://raw.githubusercontent.com/kkatayama/pianists/main/docs/search1.png](https://raw.githubusercontent.com/kkatayama/pianists/main/docs/search1.png)
**Search Parameters**
 * Song Title - can supply **all** or **parts** of a song title (not case sensitive)
   * note: submitting no title implies **return all titles**
 * Level - can select **one** or **many** levels to filter by
   * note: selecting no levels implies *return all levels*
 * Category - can select **one** or **many** categories to filter by
   * note: selecting no category implies *return all categories*

#http://localhost:8080/search# Example: Submitting No Parameters
**http://localhost:8080/search?title=**
![https://raw.githubusercontent.com/kkatayama/pianists/main/docs/search2.png](https://raw.githubusercontent.com/kkatayama/pianists/main/docs/search2.png)

## Example: Submitting Parameters
**http://localhost:8080/search?title=little&level1=Level+1&category14=Nursery+Rhyme**
![https://raw.githubusercontent.com/kkatayama/pianists/main/docs/search3.png](https://raw.githubusercontent.com/kkatayama/pianists/main/docs/search3.png)

# Download Sheet Music
Select a song title and click **Download Selected Sheet Music** to download the pdf file for the **logged in user**
**POST: http://localhost:8080/downloadFile**
**POST DATA**
```json
{ "entry_id": 207 }
```

# Dashboard Updated!
**http://localhost:8080/dashboard**
![https://raw.githubusercontent.com/kkatayama/pianists/main/docs/dashboard2.png](https://raw.githubusercontent.com/kkatayama/pianists/main/docs/dashboard2.png)

