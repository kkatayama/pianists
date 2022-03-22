<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Pianists</title>
    <link rel="stylesheet" type="text/css" href="/static/css/blueTableDashboard.css">
  </head>

  <body>
    <div class="center">
      <form method="post">
        <div class="divTable blueTable">
          <div class="divTableHeading">
            <div class="divTableRow">
              <div class="divTableHead"></div>
              <div class="divTableHead">ID</div>
              <div class="divTableHead">FILE NAME</div>
              <div class="divTableHead">DATE</div>
            </div>
          </div>
          <div class="divTableBody">
            % if defined('rows'):
              % for row in rows:
                <div class="divTableRow">
                  <div class="divTableCell">
                    <input type="radio" name="entry_id" value="{{row['entry_id']}}" checked />
                  </div>
                  <div class="divTableCell">{{row["entry_id"]}}</div>
                  <div class="divTableCell">{{row["file_name"]}}</div>
                  <div class="divTableCell">{{row["entry_time"]}}</div>
                </div>
              % end
            % end
          </div>
          <div class="divTableFoot tableFootStyle">
            <div class="divTableRow">
              <div class="divTableCell">
                <input type="submit" formaction="/deleteFile" value="Delete" />
              </div>
              <div class="divTableCell">
                <a href="/uploadFile">
                  Upload File
                </a>
              </div>
              <div class="divTableCell">
                <input type="submit" formaction="/processFile" value="Process File" />
              </div>
              <div class="divTableCell">
                <a href="/logout">
                  Log Out
                </a>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </body>
</html>
