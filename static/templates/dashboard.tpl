<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Pianists</title>
    <link rel="stylesheet" type="text/css" href="/static/css/blueTableDashboard.css">
  </head>

  <body>
    <div class="outer">
      <div class="top">
        <form method="post">
          <div class="banner">User Dashboard</div>
          <table class="greenTable" id="results">
            <thead>
              <tr>
                <th></th>
                <th>ID</th>
                <th>Title</th>
                <th>File Name</th>
                <th>Level</th>
                <th>Category</th>
                <th>Date Downloaded</th>
              </tr>
            </thead>
            <tbody>
              % if defined('rows'):
                % for row in rows:
                  <tr>
                    <td>
                      <input type="radio" name="entry_id" value="{{row['entry_id']}}" checked />
                    </td>
                    <td>{{row["entry_id"]}}</td>
                    <td>{{row["title"]}}</td>
                    <td>{{row["file_name"]}}</td>
                    <td>{{row["level"]}}</td>
                    <td>{{row["category"]}}</td>
                    <td>{{row["entry_time"]}}</td>
                  </tr>
                % end
              % end
            </tbody>
          </table>
      </div>
      <div class="below">
        <input type="submit" class="submit" formaction="/deleteFile" name="webapp" value="Delete File" />
        <input type="submit" class="submit" formaction="/processFile" name="webapp" value="Process File" />
        <a href="/search" class="submit">Find Sheet Music</a>
        <a href="/logout" class="submit">Log Out</a>
        </form>
      </div>
    </div>
  </body>
</html>
