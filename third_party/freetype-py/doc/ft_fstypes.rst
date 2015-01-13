FT_FSTYPES
==========

A list of bit flags that inform client applications of embedding and
subsetting restrictions associated with a font.

.. data:: FT_FSTYPE_INSTALLABLE_EMBEDDING

  Fonts with no fsType bit set may be embedded and permanently installed on
  the remote system by an application.


.. data:: FT_FSTYPE_RESTRICTED_LICENSE_EMBEDDING

  Fonts that have only this bit set must not be modified, embedded or exchanged
  in any manner without first obtaining permission of the font software
  copyright owner.


.. data:: FT_FSTYPE_PREVIEW_AND_PRINT_EMBEDDING

  If this bit is set, the font may be embedded and temporarily loaded on the
  remote system. Documents containing Preview & Print fonts must be opened
  'read-only'; no edits can be applied to the document.


.. data:: FT_FSTYPE_EDITABLE_EMBEDDING

  If this bit is set, the font may be embedded but must only be installed
  temporarily on other systems. In contrast to Preview & Print fonts,
  documents containing editable fonts may be opened for reading, editing is
  permitted, and changes may be saved.


.. data:: FT_FSTYPE_NO_SUBSETTING

  If this bit is set, the font may not be subsetted prior to embedding.


.. data:: FT_FSTYPE_BITMAP_EMBEDDING_ONLY

  If this bit is set, only bitmaps contained in the font may be embedded; no
  outline data may be embedded. If there are no bitmaps available in the font,
  then the font is unembeddable.

