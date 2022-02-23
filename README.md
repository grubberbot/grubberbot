## How to contribute
Any of the following will help the development of GrubberBot:
1. Make a new [Issue](https://github.com/grubberbot/grubberbot/issues)
2. Talk about existing [Issues](https://github.com/grubberbot/grubberbot/issues)
3. Fix an [Issue](https://github.com/grubberbot/grubberbot/issues)
    1. Pick an issue
    2. Make code changes and create a Pull Request
    3. Link the Pull Request to the issue
4. Accept Pull Requests
    1. Read the issue associated with the Pull Request
    2. Read the code changes, verify that the code changes meet the requirements
    3. Ask any questions you may have in the Pull Request or linked issue
5. If you are a mod:
    - If a PR looks good: accept PRs from branches to `development` (squash and merge)
    - If `master` is ahead of `development`: create and accept a PR from `master` -> `development`.
    - If `master` is behind `development`: create a PR from `development` -> `master` (modify the PR if one already exists)
    - If `development` has changes that need to be deployed quickly: create/accept a PR from `development` -> `production`

## How to create a Pull Request (PR)
1. Install [Docker](https://docs.docker.com/get-docker/)
   - Make sure docker-compose is installed by testing with the command `docker-compose version`
2. Make a branch from `development` branch.  Give it a long, descriptive name.  Make changes to the repo in your new branch
3. Test the changes by building at least one unit test in the `tests/` directory (uses `pytest`)
4. Verify style changes (uses Python 3.9)
    ```
    python -m pip install -r requirements-dev.txt
    pre-commit run --all-files
    ```
4. Run tests
    ```
    docker-compose down -v
    docker image prune --force --all
    docker-compose up --build --force-recreate --abort-on-container-exit --exit-code-from test --remove-orphans
    ```
    - Same command but on a single line:
        ```
        docker-compose down -v && docker image prune --force --all && docker-compose up --build --force-recreate --abort-on-container-exit --exit-code-from test --remove-orphans
        ```
5. Shut down Docker when you're done
    ```
    docker-compose down -v
    ```
6. Merge your changes with `development` by making a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) for review (squash and merge)

## Accepting Pull Requests
Pull Requests should only be accepted if:
- If code has changed functionality: They have created at least 1 unit test
- If code passes unit testing
- If code passes style testing
- If the PR is squashed

## How branching works
The `production` branch is code that is deployed to GrubberBot.  There are two ways that code can get to `production`:
1. The intended way: PR -> `development` -> `master` -> `production`.  The `master` branch represents the current state of GrubberBot, so Paul reviews all changes (for now).  By having PRs go through `master` the changes are slower but are reviewed.  
2. The fast way: PR -> `development` -> `production`.  Mods have the power to bypass Paul if the change is urgent.  However, the next time that `master` -> `production`, it will overwrite this temporary change.  

## TODO:
1. Database migration with Alembic
2. Ensure Docker BuildKit is enabled
3. Modify mypy.ini
