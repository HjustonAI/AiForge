#!/usr/bin/env python3
"""
FORGE Chunk Reader v0.1
Reads large files and reports statistics. Designed for files too large
for Claude's Read tool (>10k tokens).

Usage:
    python chunk-reader.py <file> --stats        # Show file stats only
    python chunk-reader.py <file> --chunk N       # Print chunk N (0-indexed, ~5000 tokens each)
    python chunk-reader.py <file> --sections      # Print section headers with line ranges
    python chunk-reader.py <file> --head N        # Print first N lines
    python chunk-reader.py <file> --tail N        # Print last N lines

Design: Zero external dependencies. Chunk size tuned for Claude's Read tool limits.
"""
import argparse
import sys

TOKEN_MULTIPLIER = 1.3
CHUNK_SIZE_WORDS = 3800  # ~5000 tokens per chunk


def estimate_tokens(text):
    """Estimate token count: words * 1.3"""
    return int(len(text.split()) * TOKEN_MULTIPLIER)


def get_stats(filepath):
    """Read file and compute all statistics."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback for Windows files with different encoding
        with open(filepath, 'r', encoding='cp1252') as f:
            content = f.read()

    lines = content.splitlines()
    words = len(content.split())
    tokens = estimate_tokens(content)

    # Find ## sections with line numbers
    sections = []
    for i, line in enumerate(lines, 1):
        if line.startswith('## '):
            sections.append((i, line.strip()))

    chunks_needed = max(1, (words + CHUNK_SIZE_WORDS - 1) // CHUNK_SIZE_WORDS)

    return {
        'lines': len(lines),
        'words': words,
        'tokens': tokens,
        'sections': sections,
        'chunks_needed': chunks_needed,
        'content': content,
        'lines_list': lines,
    }


def print_stats(stats, filepath):
    """Print file statistics summary."""
    print(f"  File: {filepath}")
    print(f"  Lines: {stats['lines']}")
    print(f"  Words: {stats['words']}")
    print(f"  Tokens (est.): {stats['tokens']}")
    print(f"  Chunks needed: {stats['chunks_needed']} (at ~5000 tokens each)")
    if stats['sections']:
        print(f"  Sections ({len(stats['sections'])}):")
        for line_num, heading in stats['sections']:
            print(f"    L{line_num}: {heading}")
    else:
        print("  Sections: none detected (no ## headings)")

    # Read tool compatibility check
    if stats['tokens'] <= 10000:
        print("  Status: fits in single Read tool call")
    else:
        print(f"  Status: TOO LARGE for Read tool — use --chunk 0..{stats['chunks_needed']-1}")


def print_chunk(stats, chunk_idx):
    """Print a specific chunk by word-boundary splitting."""
    words = stats['content'].split()
    start = chunk_idx * CHUNK_SIZE_WORDS
    end = min(start + CHUNK_SIZE_WORDS, len(words))

    if start >= len(words):
        print(f"  Chunk {chunk_idx} is out of range "
              f"(file has {stats['chunks_needed']} chunks: 0..{stats['chunks_needed']-1})",
              file=sys.stderr)
        sys.exit(1)

    chunk_text = ' '.join(words[start:end])
    chunk_tokens = estimate_tokens(chunk_text)

    print(f"--- Chunk {chunk_idx}/{stats['chunks_needed']-1} "
          f"(words {start}-{end-1}/{len(words)-1}, ~{chunk_tokens} tokens) ---")
    print(chunk_text)


def print_sections(stats):
    """Print section headers with line numbers."""
    if not stats['sections']:
        print("  No ## sections found.")
        return
    for line_num, heading in stats['sections']:
        print(f"  L{line_num}: {heading}")


def print_head(stats, n):
    """Print first N lines with line numbers."""
    for i, line in enumerate(stats['lines_list'][:n], 1):
        print(f"  {i:4d} | {line}")
    remaining = stats['lines'] - n
    if remaining > 0:
        print(f"  ... ({remaining} more lines)")


def print_tail(stats, n):
    """Print last N lines with line numbers."""
    total = len(stats['lines_list'])
    start = max(0, total - n)
    if start > 0:
        print(f"  ... ({start} lines before)")
    for i, line in enumerate(stats['lines_list'][start:], start + 1):
        print(f"  {i:4d} | {line}")


def main():
    parser = argparse.ArgumentParser(
        description='FORGE Chunk Reader — read large files in manageable pieces',
        epilog='Examples:\n'
               '  python chunk-reader.py research.md --stats\n'
               '  python chunk-reader.py research.md --chunk 0\n'
               '  python chunk-reader.py research.md --head 100 --tail 50',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('file', help='File to read')
    parser.add_argument('--stats', action='store_true',
                        help='Show file statistics (default if no other flag)')
    parser.add_argument('--chunk', type=int, metavar='N',
                        help='Print chunk N (0-indexed)')
    parser.add_argument('--sections', action='store_true',
                        help='List section headers with line numbers')
    parser.add_argument('--head', type=int, metavar='N',
                        help='Print first N lines')
    parser.add_argument('--tail', type=int, metavar='N',
                        help='Print last N lines')

    args = parser.parse_args()
    stats = get_stats(args.file)

    # Default to --stats if no specific action requested
    has_action = (args.chunk is not None or args.sections
                  or args.head is not None or args.tail is not None)

    if args.stats or not has_action:
        print_stats(stats, args.file)

    if args.sections:
        print_sections(stats)

    if args.chunk is not None:
        print_chunk(stats, args.chunk)

    if args.head is not None:
        print_head(stats, args.head)

    if args.tail is not None:
        print_tail(stats, args.tail)


if __name__ == '__main__':
    main()
