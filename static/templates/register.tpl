<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Pianists</title>
    <link rel="stylesheet" type="text/css" href="/static/css/blueTableIndex.css">
  </head>

  <body>
    <div class="center">
      <form action="/createUser" method="post">
        <div class="divTable blueTable">
          <div class="divTableBody">
            % if defined('res'):
              % for key,value in res.items():
                <div class="divTableRow">
                  <div class="divTableCell">
                    "{{key}}": "{{value}}"
                  </div>
                </div>
              % end
            % end
            <div class="divTableRow">
              <div class="divTableCell">
                <input name="username" type="text" placeholder="Username" />
              </div>
            </div>
            <div class="divTableRow">
              <div class="divTableCell">
                <input name="password" type="password" placeholder="Password" />
              </div>
            </div>
            <div class="divTableRow">
              <div class="divTableCell">
                <input name="password2" type="password" placeholder="Password Again" />
              </div>
            </div>
          </div>
          <div class="divTableFoot tableFootStyle">
            <div class="divTableRow">
              <div class="divTableCell">
                <div class="divTableCellLeft"><input type="submit" name="webapp" value="Submit" /></div>
                <div class="divTableCellRight"><a href="/login">Back to Login</a></div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </body>
</html>
