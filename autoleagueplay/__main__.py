"""AutoLeague

Usage:
    autoleagueplay setup <working_dir>
    autoleagueplay (odd | even) [--replays=R|--list|--results|--test|--record]
    autoleagueplay test
    autoleagueplay fetch <week_num>
    autoleagueplay leaderboard (odd | even)
    autoleagueplay leaderboard (clip | symbols | legend)
    autoleagueplay (-h | --help)
    autoleagueplay --version

Options:
    --replays=R                  What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: calculated_gg]
    --list                       Instead of playing the matches, the list of matches is printed.
    --results                    Like --list but also shows the result of matches that has been played.
    --test                       Checks if all needed bots are in the bot folder.
    --record                     Record matches with ffmpeg.
    -h --help                    Show this screen.
    --version                    Show version.
"""

import sys
from pathlib import Path

from docopt import docopt

from autoleagueplay.leaderboard.leaderboard import generate_leaderboard, generate_leaderboard_clip
from autoleagueplay.leaderboard.symbols import generate_symbols, generate_legend
from autoleagueplay.list_matches import list_matches
from autoleagueplay.load_bots import check_bot_folder
from autoleagueplay.paths import WorkingDir
from autoleagueplay.replays import ReplayPreference
from autoleagueplay.run_matches import run_league_play
from autoleagueplay.settings import PersistentSettings
from autoleagueplay.sheets import fetch_ladder_from_sheets
from autoleagueplay.version import __version__


def main():
    arguments = docopt(__doc__, version=__version__)
    settings = PersistentSettings.load()

    if arguments['setup']:
        working_dir = Path(arguments['<working_dir>'])
        working_dir.mkdir(exist_ok=True, parents=True)
        WorkingDir(working_dir)   # Creates relevant directories and files
        settings.working_dir_raw = f'{working_dir}'
        settings.save()
        print(f'Working directory successfully set to \'{working_dir}\'')

    else:
        # Following commands require a working dir. Make sure it is set.
        if settings.working_dir_raw is None:
            print('No working directory set, use \'autoleagueplay setup <working_dir>\'')
            sys.exit(0)

        working_dir = WorkingDir(Path(settings.working_dir_raw))

        if arguments['leaderboard']:
            if arguments['odd'] or arguments['even']:
                generate_leaderboard(working_dir, arguments['odd'])
            elif arguments['clip']:
                generate_leaderboard_clip(working_dir)
            elif arguments['symbols']:
                generate_symbols()
            elif arguments['legend']:
                generate_legend(working_dir)
            else:
                raise NotImplementedError()

        elif arguments['odd'] or arguments['even']:

            replay_preference = ReplayPreference(arguments['--replays'])

            if arguments['--results']:
                list_matches(working_dir, arguments['odd'], True)
            elif arguments['--list']:
                list_matches(working_dir, arguments['odd'], False)
            elif arguments['--test']:
                check_bot_folder(working_dir, arguments['odd'])
            else:
                run_league_play(working_dir, arguments['odd'], replay_preference, arguments['--record'])

        elif arguments['test']:
            check_bot_folder(working_dir)

        elif arguments['fetch']:
            week_num = int(arguments['<week_num>'])
            if week_num < 0:
                print(f'Week number must be a positive integer.')
                sys.exit(1)

            ladder = fetch_ladder_from_sheets(week_num)
            ladder.write(working_dir.ladder)

            print(f'Successfully fetched week {week_num} to \'{working_dir.ladder}\':')
            for bot in ladder.bots:
                print(bot)

        else:
            raise NotImplementedError()


if __name__ == '__main__':
    main()
