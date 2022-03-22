<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Pianists</title>
    <link rel="stylesheet" type="text/css" href="/static/css/blueTableDelay.css">
  </head>

  <body>
    <div class="center">
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
        </div>
      </div>
    </div>
    <script>
    % if defined('location'):
      setTimeout(function () { window.location.href="{{location}}" }, 5000);
    % end
    </script>
  </body>
</html>
