// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract RareProtocolMock is ERC721, ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;
    uint256 private _totalSupply;

    event Minted(address indexed to, uint256 indexed tokenId, string tokenURI);

    constructor() ERC721("RareProtocolMock", "RPMock") Ownable(msg.sender) {}

    function mint(
        address to,
        string calldata tokenURI_,
        bytes calldata /* metadata */
    ) external onlyOwner returns (uint256 tokenId) {
        tokenId = _nextTokenId++;
        _totalSupply++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI_);
        emit Minted(to, tokenId, tokenURI_);
    }

    function totalSupply() external view returns (uint256) {
        return _totalSupply;
    }

    // Override required by Solidity when inheriting both ERC721 and ERC721URIStorage
    function tokenURI(
        uint256 tokenId_
    ) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId_);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
