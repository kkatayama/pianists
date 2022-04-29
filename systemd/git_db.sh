#!/bin/bash

inotifywait -q -m -e CLOSE_WRITE --format="git commit -m 'auto commit db' %w && git push origin main" ../pianists.db | bash
