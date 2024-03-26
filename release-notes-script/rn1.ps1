param (
    [string]$repository = $(throw "-repository is required"),
    [string]$previousVersion = $(throw "-oldCommitId is required"),
    [string]$targetVersion = $(throw "-newCommitId is required"),
    [String]$SecretValue
)
 
 
$gitHist = (git log --format="%ai`t%an`t%s" "$previousVersion...$targetVersion") | ConvertFrom-Csv -Delimiter "`t" -Header ("Date","Author","Subject")
# $gitHist
$array_urls = @()
foreach($line in $gitHist)
{
    if($line.Subject -match 'NEX( |-)(\d)*' ){
        $jira_url = "https://revenuesolutions.atlassian.net/browse/$($Matches[0].toUpper().replace(' ','-'))"
        #Write-host "adding...: $jira_url"
        $array_urls += $jira_url
    }elseif($line.Subject -match '\(#((\d)*)\)'){
        $apiurl = "https://api.github.com/repos/revenue-solutions-inc/$repository/pulls/$($Matches[1])"
        $response = invoke-restMethod $apiurl  -headers @{Authorization = "bearer $SecretValue"}
        $source_branch = $response.head.ref
        if($source_branch -match 'NEX( |-)(\d)*'){
            $jira_url = "https://revenuesolutions.atlassian.net/browse/$($Matches[0].toUpper().replace(' ','-'))"
            #Write-host "adding..............: $jira_url"
            $array_urls += $jira_url
        }
    }
}
$UniqueArray = $array_urls | Sort-Object | Get-Unique
$UniqueArray