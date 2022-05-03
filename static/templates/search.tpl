<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Pianists</title>
    <link rel="stylesheet" type="text/css" href="/static/css/blueTableSearch.css">
  </head>

  <body>
    <div class="outer">
      <div class="top">
        <form action="/search" method="get" id="search">
          <div class="divTable blueTable">
            <div class="divTableRow">
              % if user_values.get('title'):
              <input type="text" name="title" placeholder="Song Title" value="{{user_values['title']}}" />
              % else:
              <input type="text" name="title" placeholder="Song Title" />
              % end
            </div>
            <div class="divTableRow">
              % for i, level in enumerate(levels):
              <div class="divTableCellLevel">
                % if user_values.get('level'):
                % if f'level{i+1}' in user_values['level']:
                <input type="checkbox" id="level{{i+1}}" name="level{{i+1}}" value="Level {{i+1}}" checked />
                % else:
                <input type="checkbox" id="level{{i+1}}" name="level{{i+1}}" value="Level {{i+1}}" />
                % end
                % else:
                <input type="checkbox" id="level{{i+1}}" name="level{{i+1}}" value="Level {{i+1}}" />
                % end
                <label for="level{{i+1}}"> Level {{i+1}} </label>
              </div>
              % end
            </div>
            <div class="divTableRow">
              % for i, cat in enumerate(categories):
              <div class="divTableCellCategory">
                % if user_values.get('category'):
                % if f'category{i+1}' in user_values['category']:
                <input type="checkbox" id="category{{i+1}}" name="category{{i+1}}" value="{{cat["category"]}}" checked />
                % else:
                <input type="checkbox" id="category{{i+1}}" name="category{{i+1}}" value="{{cat["category"]}}" />
                % end
                % else:
                <input type="checkbox" id="category{{i+1}}" name="category{{i+1}}" value="{{cat["category"]}}" />
                % end
                <label for="category{{i+1}}"> {{cat["category"]}} </label>
              </div>
              <!-- % if (i+1) % 6 == 0: -->
              <!--   <br /> -->
              <!-- % end -->
              % end
            </div>
          </div>
          <input type="submit" class="submit" name="webapp" value="Search Piano Sheet Music" />
        </form>
      </div>
      <div class="below">
        % if defined('rows'):
        <form action="/downloadFile" method="post">
          <div class="banner">Search Results</div>
          <table class="greenTable" id="results">
            <thead>
              <tr>
                <th></th>
                <th>Title</th>
                <th>Level</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              % for i, row in enumerate(rows):
              <tr>
                <td>
                  % if i == 0:
                  <input type="radio" name="entry_id" value="{{row['entry_id']}}" checked />
                  % else:
                  <input type="radio" name="entry_id" value="{{row['entry_id']}}" />
                  % end
                </td>
                <td>{{row["title"]}}</td>
                <td>{{row["level"]}}</td>
                <td>{{row["category"]}}</td>
              </tr>
              % end
            </tbody>
          </table>
          % if len(rows):
            <input type="submit" class="submit" name="webapp" value="Download Selected Sheet Music" />
          % end
        </form>
        % end
      </div>
    </div>
  </body>
</html>
