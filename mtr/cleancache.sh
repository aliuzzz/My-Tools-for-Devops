#!/bin/bash
sync
  sleep 1
echo 1 > /proc/sys/vm/drop_caches
  sleep 1
echo 2 > /proc/sys/vm/drop_caches
  sleep 1
echo 3 > /proc/sys/vm/drop_caches
  sleep 1
echo 0 > /proc/sys/vm/drop_caches

