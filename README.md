# AIWarSoc Common
The common code and data shared by the other modules. 

Contains:

- A python repository defining the database tables and connection methods, as well as a config file parser and gamemode definitions
- A default_config.yml file used by many other modules, which gives all of the available config options and their defaults

## Usage

### Python

You can add the python module using `pip install cuwais-common`

From there you can use a database connection in the following way:

```python
with cuwais.database.create_session() as db_session:
  user_scores = db_session.query(
    User,
    func.sum(Result.points_delta).label("total_score")
  ).outerjoin(User.submissions) \
  .outerjoin(Submission.results) \
  .group_by(User.id) \
  .order_by("total_score") \
  .all()
```

or get a gamemode and all of its data by using `Gamemode.get(‘game-name’)`

### Config

The default config file can be got using `wget default_config.yml https://raw.githubusercontent.com/AI-Wars-Soc/common/main/default_config.yml`

## Contributing

First ensure that you have read all of the Contributing rules within the `server` repository. If you do not set up your contribution environment correctly then you may end up missing a step.

### Gamemodes

The most common way of contributing to this repository is to add a new gamemode. A gamemode describes a possible game that can be used in a competition, eg. chess.

To add a new gamemode you must do the following:

- Add any libraries required by your gamemode to `setup.py`
- Add a new class which implements the abstract class `Gamemode` within `gamemodes.py`
- Allow your gamemode to be found by adding it to the `get(gamemode_name: str)` function in the `Gamemode` class.

Once you have done this, it will be possible for AIs to be written and battled for your new game. HOWEVER this does not mean that your game is fully implemented! You must also ensure that the `sandbox` docker image contains all of the libraries that you have used in your gamemode, and if you want your game to be playable in the browser then you must also add rendering code to `web-app`. Head to both of these repositories to find relevant contribution instructions.

### Config

The other way of contributing to this repository is by adding options to the `default_config.yml` file. This file is included in the build step of all relevant docker images, so the only tricky bit to remember when contributing here is that you must ensure that you merge your updates to the `default_config.yml` file here before you merge your updates to whatever needs the new config options. That way the `default_config.yml` file will be the new version when your new changes in the other modules are built.

Along the same lines, if you change a default value then all of the modules that use that value must be rebuilt so that they are aware of the change. 