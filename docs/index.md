# PFS Target Database

Welcome to the documentation for the PFS Target Database. This database is designed to store and manage targets for the [Subaru Prime Focus Spectrograph (PFS)](https://pfs.ipmu.jp/) observations.

## Overview

The PFS Target Database stores information about targets for science observations as well as calibration objects.  The database also contains information about observation proposals and the filters used for quality assurance.

The database is implemented in PostgreSQL built with Python/SQLAlchemy. It also includes a set of command-line tools hopefully useful for database management and science operations.

We hope this documentation will be a valuable resource as you work with the PFS Target Database. If you have any questions or feedback, please don't hesitate to [contact us](contact.md).

## License

This package is distributed under the MIT License.

```
Copyright (c) 2021 Masato Onodera

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
