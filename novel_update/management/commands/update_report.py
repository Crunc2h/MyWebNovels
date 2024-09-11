from django.core.management.base import BaseCommand
from datetime import datetime, timezone, timedelta
from time import sleep
import enums_configs.models as ec_models
import enums_configs.native.novel_processor_cfg as np_cfg
import novel_processor.models as np_models
import novel_storage.models as ns_models
import novel_scraper.native.cout_custom as cout
import os


class Command(BaseCommand):
    help = "DBWideReset"

    def handle(self, *args, **options):
        pool = np_models.NovelProcessPool.objects.first()
        t_init = datetime.now(timezone.utc)
        t_wait = 2
        loader = cout.COutLoading()
        total_processes = pool.processes.count()
        links = ns_models.TempNovelLink.objects.count()
        np_speeds = [0]
        ncp_speeds = [0]
        ncu_speeds = [0]
        while True:
            os.system("clear")
            processes = pool.processes.all()
            t_elapsed = (datetime.now(timezone.utc) - t_init).seconds / 60
            processes_unchecked_by_novel_profiler = len(
                list(
                    filter(
                        lambda process: (
                            datetime.now(timezone.utc)
                            - process.last_processed_by_novel_profiler
                        ).seconds
                        // 60
                        > np_cfg.PROCESS_CONTROL_THRESHOLD,
                        processes,
                    )
                )
            )
            processes_unchecked_by_novel_chapter_profiler = len(
                list(
                    filter(
                        lambda process: (
                            datetime.now(timezone.utc)
                            - process.last_processed_by_novel_chapter_profiler
                        ).seconds
                        // 60
                        > np_cfg.PROCESS_CONTROL_THRESHOLD,
                        processes,
                    )
                )
            )
            processes_unchecked_by_novel_chapter_updater = len(
                list(
                    filter(
                        lambda process: (
                            datetime.now(timezone.utc)
                            - process.last_processed_by_novel_chapter_updater
                        ).seconds
                        // 60
                        > np_cfg.PROCESS_CONTROL_THRESHOLD,
                        processes,
                    )
                )
            )

            if processes_unchecked_by_novel_profiler > 0:
                np_speed = (
                    (total_processes - processes_unchecked_by_novel_profiler)
                    / t_elapsed
                    if t_elapsed > 1.0
                    else (total_processes - processes_unchecked_by_novel_profiler) / 1
                )
                np_speeds.append(np_speed)
            if processes_unchecked_by_novel_chapter_profiler > 0:
                ncp_speed = (
                    (total_processes - processes_unchecked_by_novel_chapter_profiler)
                    / t_elapsed
                    if t_elapsed > 1.0
                    else (
                        total_processes - processes_unchecked_by_novel_chapter_profiler
                    )
                    / 1
                )
                ncp_speeds.append(ncp_speed)
            if processes_unchecked_by_novel_chapter_updater > 0:
                ncu_speed = (
                    (total_processes - processes_unchecked_by_novel_chapter_updater)
                    / t_elapsed
                    if t_elapsed > 1.0
                    else (
                        total_processes - processes_unchecked_by_novel_chapter_updater
                    )
                    / 1
                )
                ncu_speeds.append(ncu_speed)

            np_time_left = (
                0.0
                if np_speed < 1
                else processes_unchecked_by_novel_profiler / np_speed
            )
            ncp_time_left = (
                0.0
                if ncp_speed < 1
                else processes_unchecked_by_novel_chapter_profiler / ncp_speed
            )
            ncu_time_left = (
                0.0
                if ncu_speed < 1
                else processes_unchecked_by_novel_chapter_updater / ncu_speed
            )
            cout.COut.broadcast(
                f"\n\
 {loader.load()} Total number of links gathered: {links}\n\
 {loader.load()} Total number of processes: {total_processes}\n\
 {loader.load()} Current active processes: {pool.processes.filter(is_being_processed=True).count()}\n\
 {loader.load()} Processes unchecked by novel profiler: {processes_unchecked_by_novel_profiler} ({'{:.2f}'.format(np_speed)}/min) ({'{:.2f}'.format(sum(np_speeds)/len(np_speeds))}/min avg.) {f'{'{:.2f}'.format(np_time_left)} mins left' if processes_unchecked_by_novel_profiler > 0 else 'All processes are updated'}\n\
 {loader.load()} Processes unchecked by novel chapter profiler: {processes_unchecked_by_novel_chapter_profiler} ({'{:.2f}'.format(ncp_speed)}/min) ({'{:.2f}'.format(sum(ncp_speeds)/len(ncp_speeds))}/min avg.) {f'{'{:.2f}'.format(ncp_time_left)} mins left' if processes_unchecked_by_novel_chapter_profiler > 0 else 'All processes are updated'}\n\
 {loader.load()} Processes unchecked by novel chapter updater: {processes_unchecked_by_novel_chapter_updater} ({'{:.2f}'.format(ncu_speed)}/min) ({'{:.2f}'.format(sum(ncu_speeds)/len(ncu_speeds))}/min avg.) {f'{'{:.2f}'.format(ncu_time_left)} mins left' if processes_unchecked_by_novel_chapter_updater > 0 else 'All processes are updated'}\n\
 {loader.load()} Time elapsed: {'{:.2f}'.format(t_elapsed)} minutes",
                style="success",
                header="DB_REPORT",
            )
            sleep(t_wait)
