"""Logging configuration and handler management.

This module provides utilities for configuring standard library loggers to use loguru as the
underlying logging backend. It includes a custom logging handler that bridges the standard library
logging interface with loguru's enhanced logging capabilities, as well as configuration parsing and
logger lifecycle management.
"""

from __future__ import annotations

import json
import logging
import sys
from traceback import format_exception
from typing import TYPE_CHECKING, Any

import loguru

import walker.config as wc
from walker.api import attrs
from walker.config import Config, ConfigKey, ConfigValue, NoDefault

if TYPE_CHECKING:
    from loguru import Record as LogRecord

# Ensure the default handler added by Loguru is removed
loguru.logger.remove()


class _LoguruHandler(logging.Handler):
    """Custom logging handler that delegates to loguru.

    This handler bridges the standard library :py:class:`logging.Logger` interface with loguru's
    enhanced logging capabilities. It converts standard logging records into loguru log messages.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emits a logging record to loguru.

        This method is called by the logging framework when a record is ready to be logged. It
        extracts the log level and message from the record and delegates to loguru for processing.

        :param record: the logging record to be emitted.
        """
        logger_opt = loguru.logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def parse_logger_option(name: ConfigKey, value: ConfigValue) -> ConfigValue:
    """Parses and validates logger configuration options.

    This function processes individual logger configuration entries, performing type conversion and
    validation.

    :param name: the configuration key being parsed.
    :param value: the configuration value to be parsed.
    :returns: the parsed and validated configuration value, potentially transformed from its
        original form.
    :raises ValueError: the logging destination is invalid or missing.
    """
    match name:
        case attrs.config.Logging.DESTINATION:
            if value in ("-", None):
                value = sys.stdout
            if value is NoDefault:
                raise ValueError("Logging destination must be provided")

    return value


def format_log_record(log_record: LogRecord) -> str:
    """Formats a Loguru log record as a compact JSON string.

    Produces a single-line JSON object suitable for structured logging. If an exception is attached
    to the record, its formatted traceback is included.

    :param log_record: the Loguru log record to format.
    :returns: a JSON-encoded log entry terminated by a newline character.
    """
    log_structured: dict[str, Any] = {
        "message": log_record["message"],
        "level": log_record["level"].name.lower(),
        "time": log_record["time"].isoformat(),
        "process": log_record["process"].id,
        "module": log_record["name"],
        "function": log_record["function"],
        "line": log_record["line"],
    }
    log_record_exception = log_record["exception"]
    if log_record_exception is not None:
        log_structured["exception"] = format_exception(
            log_record_exception.type, log_record_exception.value, log_record_exception.traceback
        )

    log_record["extra"]["serialized"] = json.dumps(log_structured, separators=(",", ":"))
    return "{extra[serialized]}\n"


def configure_logger(logger: logging.Logger, logger_config: Config) -> None:
    """Configures a standard library logger to defer all logging operations to loguru.

    :param logger: the standard library logger to configure.
    :param logger_config: configuration dictionary containing logger options.
    """
    logger_options: Config = {}
    for option_name, option_value in logger_config.items():
        logger_options[option_name] = parse_logger_option(option_name, option_value)

    logger_destination = logger_options.pop(attrs.config.Logging.DESTINATION)
    logger_structured = logger_options.pop(attrs.config.Logging.STRUCTURED, False)
    if logger_structured:
        loguru.logger.add(logger_destination, format=format_log_record, **logger_options)
    else:
        loguru.logger.add(logger_destination, **logger_options)

    redirect_logger(logger, logger_level=wc.get(logger_options, attrs.config.Logging.LEVEL))


def deactivate_logger(logger: logging.Logger) -> None:
    """Deactivates a logger by removing all of its handlers."""
    logger.handlers.clear()


def redirect_logger(logger: logging.Logger, logger_level: int | str) -> None:
    """Redirects a standard library logger to Loguru.

    All existing handlers are removed before attaching the new one, ensuring logs are exclusively
    routed through Loguru without duplication.

    :param logger: the standard library logger to redirect.
    :param logger_level: the logging level to set on the logger and its handler.
    """
    # Remove all logger handlers to only redirect logs to Loguru
    deactivate_logger(logger)

    logger.setLevel(logger_level)
    logger.addHandler(_LoguruHandler(logger_level))


__all__ = ["configure_logger", "deactivate_logger", "redirect_logger"]
