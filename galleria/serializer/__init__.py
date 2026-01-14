"""Galleria internal data models for photo collections.

This module provides typed models (Photo, PhotoCollection) intended to be
galleria's internal representation of photo data, separate from external
formats like NormPic manifests.

STATUS: Incomplete infrastructure for galleria extraction (~v0.3).

Currently, the NormPicProviderPlugin returns plain dicts instead of these
typed models. Before extracting galleria as a standalone project, decide:
  1. Have plugins return typed models for type safety, or
  2. Remove this module and use dict-based plugin contracts

See doc/TODO.md "Galleria Extraction Preparation" for context.
"""
