# Co-authored-by satirini kaldir + GitHub'a push et
# Cursor disi terminalde calistir:  powershell -ExecutionPolicy Bypass -File ai/fix-commit.ps1

Set-Location (Split-Path $PSScriptRoot -Parent)

git config alias.ct commit-tree

$msg = @"
Add Sprint 1 AI POC with docs and sample plant images.

Includes Groq vision/sentiment scripts, research docs, and three sample photos for image recognition testing.
"@

$msg | Out-File -Encoding utf8NoBOM .git/COMMIT_EDITMSG_CLEAN

$tree = git rev-parse "HEAD^{tree}"
$parent = git rev-parse "HEAD~1"
$new = git ct $tree -p $parent -F .git/COMMIT_EDITMSG_CLEAN

git reset --hard $new

Write-Host "`nCommit mesaji:"
git log -1 --format="%B"

git push --force-with-lease origin ai/dev5-melike

Write-Host "`nTamam. GitHub'da cursoragent artik gorunmemeli."
