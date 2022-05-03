<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Pianists</title>
    <link rel="stylesheet" type="text/css" href="/static/css/blueTableUpload.css">
  </head>

  <body>
    <div class="center">
      <form action="/uploadFile" method="post" enctype="multipart/form-data">
        <div class="divTable blueTable">
          <div class="divTableBody">
            <div class="divTableRow">
              <div class="divTableCell">
                <input type="file" id="upload" name="upload" accept="application/pdf" />
              </div>
            </div>
          </div>
          <div class="divTableFoot tableFootStyle">
            <div class="divTableRow">
              <div class="divTableCell">
                <input type="submit" formaction="/uploadFile" name="webapp" value="Upload File" />
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </body>
</html>
